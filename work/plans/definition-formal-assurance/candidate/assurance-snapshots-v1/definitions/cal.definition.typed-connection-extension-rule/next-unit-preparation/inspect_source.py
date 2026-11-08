"""Exact current C29 Craft Method source-only preparation; no next native interpretation."""
from pathlib import Path
import json,sys,ast,copy
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent));import build_candidate as b
snap=b.snapshot();source=b.source_ref(snap,'CAV2-D20');doc=b.co.source_document(snap,source);dp=b.ROOT/'docs/decisions/0029-cml07-semantic-foundation-v1/decision.json';decision=json.loads(dp.read_bytes());ap=dp.with_name('authorization.json');auth=json.loads(ap.read_bytes())
paths={'source':b.ROOT/source['path'],'projection':(b.ROOT/source['path']).with_name('DEFINITION.md'),'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_snapshot':b.BASE/'current-snapshot.json','checker':P/'inspect_source.py','C29_decision':dp,'C29_authorization':ap,'C29_manifest':b.ROOT/auth['manifest']['path'],'C29_validation':b.ROOT/auth['validation_receipt']['path'],'C29_Craft_candidate':b.ROOT/decision['admitted_definition_candidates'][0]['path'],'C29_selected_chain':b.ROOT/decision['selected_chain']['path']}
refs={k:b.ref(v) for k,v in paths.items()};checks=[]
def ck(n,ok):assert ok,n;checks.append({'check_id':n,'result':True})
row=next(x for x in snap['current_entries'] if x['definition_id']==source['definition_id'])
ck('exact-current-C29-Craft-Method',source['version_ref']=='CAV2-D20@1.0.0-candidate.1' and source['sha256']==refs['source']['sha256']=='f99635daec1bb7f3df027f6aa7bcfbcd0e14f1d20a700e93588dfb6268112a17' and row['term']=='Craft Method' and row['effective_state']=='admitted-current' and row['admission_decision_ref']==decision['decision_id']=='CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1')
ck('original183189201scope',len(snap['current_entries'])==183 and len(snap['historical_entries'])==6 and b.r.verify(snap,b.ROOT)['files']==201)
ck('C29-authorization-bytes',refs['C29_authorization']['sha256']==decision['authority_basis']['authorization_sha256'])
ck('C29-manifest-bytes',refs['C29_manifest']['sha256']==auth['manifest']['sha256'])
ck('C29-validation-bytes',refs['C29_validation']['sha256']==auth['validation_receipt']['sha256'] and auth['validation_receipt']['required_result']=='PASS')
ck('C29-Craft-candidate-bytes',refs['C29_Craft_candidate']['sha256']==decision['admitted_definition_candidates'][0]['sha256'])
ck('C29-selected-current-chain-bytes',refs['C29_selected_chain']['sha256']==decision['selected_chain']['sha256'] and decision['selected_chain']['decision_overlay_status']=='selected-current')
ck('C29-construction-evaluable-not-executed',decision['admission_result']['s2_posture']=='evaluable-not-executed' and decision['admission_result']['implementation_bindings_accepted']==decision['admission_result']['identity_carriers_admitted']==0)
ck('C29-positive-semantic-effects-preserved',decision['admission_result']['definitions_admitted']==14 and decision['admission_result']['artifact_types_admitted']==1 and decision['admission_result']['owner_bindings_admitted']==4 and decision['admission_result']['selected_construction_chains']==1)
ck('Definition-schema-binding',doc['schema_digest']==refs['Definition_schema']['sha256'])
ck('Definition-generator-binding',doc['source_direction']['generator_sha256']==refs['Definition_generator']['sha256'])
ck('Definition-shape',not list(b.c.Draft202012Validator(json.loads(paths['Definition_schema'].read_bytes())).iter_errors(doc)))
nodes=[x for x in ast.parse(paths['Definition_generator'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in ['esc','bullets','render']];ck('only-three-pure-functions',len(nodes)==3);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['Definition_generator']),'exec'),ns);before=copy.deepcopy(doc);one=ns['render'](doc).encode();two=ns['render'](doc).encode();ck('two-exact-projections-no-mutation',one==two==paths['projection'].read_bytes() and before==doc)
f=doc['voices']['scientific_formal'];norm=f['normative_statement'];formal=f['formal_expression']
ck('specializes-Method-recursive-chain-not-ledger',all(x in norm for x in ['specializes Method','recursive construction chain','typed identity','canonical source authority','separate construction and conformance','generated-view derivation','typed residue','child-to-parent recomposition','owner-controlled closure','ledger preserves continuity but is not the Method']))
ck('eleven-tuple-coordinates',formal=='M_Craft(S) = (context, product_intent, domain_meaning, system_specification, realization_selection, construction, conformance, operation, recovery_and_evolution, owner_continuation, ledger_state).')
ck('prerequisite-residue-and-separated-claims',all(x in f['boundary_conditions'][0] for x in ['CAV2-D65','typed prerequisite residue']) and all(x in f['boundary_conditions'][1] for x in ['Construction','conformance','runtime evidence','adoption','permission']) and 'directionally distinct' in f['boundary_conditions'][2])
ck('three-source-tests',len(f['testable_conditions'])==3 and all(x in ' '.join(f['testable_conditions']) for x in ['exact predecessor evidence','deterministically','type and owner route']))
up=[]
for i,e in enumerate(doc['source_refs']):
 if e['source_ref'].startswith('cal.definition.'):
  r=b.source_ref(snap,e['source_ref'].split('@')[0]);q=b.ROOT/r['path'];ck('exact-local-upstream-'+str(i),r['version_ref']==e['source_ref'] and r['sha256']==b.r.digest(q.read_bytes())==e['content_sha256']);refs['upstream-'+str(i)]=b.ref(q);up.append({'embedded_source_ref':e,'exact_local_ref':refs['upstream-'+str(i)],'whole_theory_imported':False})
 else:up.append({'embedded_source_ref':e,'external_bytes_read':False,'external_currentness':'pending-next-native-source-inspection','whole_theory_imported':False})
ck('three-distinct-upstream-references',len(up)==3)
ck('body-historical-chain-evidence-retained','CAL-CML07-CRAFT-IDENTITY-CHAIN-0001' in doc['evidence_refs'] and decision['selected_chain']['chain_id']=='CAL-CML07-CRAFT-IDENTITY-CHAIN-0002')
ck('method-binding-consumer-routes-kept-separate',doc['primary_consumer_refs']==['authority/artifact-types/method-binding/v1','product/products/craft/v1/method-binding.json'])
ck('next-native-absent',not (b.BASE/'definitions/CAV2-D20').exists())
b.unchanged(list(refs.values()));ck('all-inputs-current',b.r.verify(snap,b.ROOT)['files']==201)
report={'schema_version':'definition-assurance-next-source-inspection/v1-candidate','authority_effect':'none','source':source,'source_units':len(b.co.inventory(doc)),'checks':checks,'selected_inputs':refs,'upstream_observations':up,'projection_bytes':len(one),'projection_sha256':b.r.digest(one),'external_file_refs':[],'requires_TypedConnectionExtension_full_delivery_audit_first':True,'actual_next_unit_created':False,'interpretation_or_models_created':False,'native_or_live_consumer_executed':False,'actual_recursive_construction_closure_or_authority_created':False,'semantic_ready':False,'mechanized_proof':False}
if '--write' in sys.argv:
 with (P/'source-inspection.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
else:assert b.r.same_json(report,json.loads((P/'source-inspection.json').read_bytes()))
print(json.dumps({'result':'PASS-next-C29-CAV2-D20-CraftMethod-source-only','checks':len(checks),'source_units':report['source_units'],'projection_bytes':len(one),'upstream_refs':len(up),'external_upstream_currentness':'pending','actual_next_unit_created':False},indent=2))


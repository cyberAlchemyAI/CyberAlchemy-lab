"""Exact C64 Typed Connection Extension Rule source-only preparation; no next T."""
from pathlib import Path
import sys,json,ast,copy
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent));import build_candidate as b
snap=b.snapshot();assert b.r.verify(snap,b.ROOT)['files']==201;source=b.source_ref(snap,'cal.definition.typed-connection-extension-rule');doc=b.co.source_document(snap,source);dp=b.ROOT/'docs/decisions/0064-typed-connection-extension-rule-admission/decision.json';decision=json.loads(dp.read_bytes());ap=dp.with_name('authorization.json');auth=json.loads(ap.read_bytes())
paths={'source':b.ROOT/source['path'],'projection':(b.ROOT/source['path']).with_name('DEFINITION.md'),'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_snapshot':b.BASE/'current-snapshot.json','checker':P/'inspect_source.py','C64_decision':dp,'C64_authorization':ap,'C64_candidate':b.ROOT/auth['candidate']['path'],'C64_validation':b.ROOT/auth['validation_receipt']['path']}
refs={k:b.ref(v) for k,v in paths.items()};checks=[]
def ck(n,ok):assert ok,n;checks.append({'check_id':n,'result':True})
row=next(x for x in snap['current_entries'] if x['definition_id']==source['definition_id'])
ck('exact-current-C64-source',source['sha256']==refs['source']['sha256']=='9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962' and row['effective_state']=='admitted-current' and row['admission_decision_ref']==decision['decision_id']=='CAL-DECISION-0064-TYPED-CONNECTION-EXTENSION-RULE-ADMISSION')
ck('original183189201scope',len(snap['current_entries'])==183 and len(snap['historical_entries'])==6)
ck('C64-exact-selected-definition',all(decision['admitted_definition'][k]==source[k] for k in ['path','sha256']) and decision['admitted_definition']['definition_ref']==source['version_ref'])
ck('C64-authorization-binding',refs['C64_authorization']['sha256']==decision['authorization']['sha256'])
ck('C64-candidate-binding',refs['C64_candidate']['sha256']==auth['candidate']['sha256'])
ck('C64-validation-binding',refs['C64_validation']['sha256']==auth['validation_receipt']['sha256'])
ck('C64-no-consumer-relation-or-pair-effects',decision['admission_result']['consumer_activations']==decision['admission_result']['relation_kinds_admitted']==decision['admission_result']['endpoint_pairs_admitted']==0)
ck('Definition-schema-binding',doc['schema_digest']==refs['Definition_schema']['sha256'])
ck('Definition-generator-binding',doc['source_direction']['generator_sha256']==refs['Definition_generator']['sha256'])
ck('Definition-shape',not list(b.c.Draft202012Validator(json.loads(paths['Definition_schema'].read_bytes())).iter_errors(doc)))
nodes=[x for x in ast.parse(paths['Definition_generator'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in ['esc','bullets','render']];ck('three-pure-functions-only',len(nodes)==3);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['Definition_generator']),'exec'),ns);before=copy.deepcopy(doc);one=ns['render'](doc).encode();two=ns['render'](doc).encode();ck('two-exact-projections-no-mutation',one==two==paths['projection'].read_bytes() and before==doc)
f=doc['voices']['scientific_formal'];norm=f['normative_statement'];formal=f['formal_expression']
ck('finite-closed-exact-ordered-connection-genus','finite closed set of exact ordered source-kind to target-kind connections' in norm)
ck('effective-predecessor-and-exact-successor',all(x in norm for x in ['effective predecessor Relation Kind version','exact successor contract version']))
ck('pair-specific-qualifier-values-and-constraints','pair-specific values and constraints' in norm and 'PairQualifierSchema' in formal)
ck('same-semantic-question-or-distinct-kind',all(x in norm for x in ['same unique semantic question','distinct Relation Kind']))
ck('local-scope-not-global-pair',all(x in formal for x in ['Local(o,s,t) does not imply','Register(k) does not imply']))
ck('instance-conformance-admitted-effective-contract','exact contract is admitted and effective' in formal)
ck('no-registration-cartesian-wildcard-observation-inference',all(x in norm for x in ['endpoint registration','separate source and target lists','wildcard matching','historical observation','local graph use','candidate validation','second writable projection']))
ck('canonical-TypedRelation-or-specialized-authority','{TypedRelation, SpecializedCarrier}' in formal)
ck('nine-boundaries-twelve-tests',len(f['boundary_conditions'])==9 and len(f['testable_conditions'])==12)
upstreams=[]
for i,e in enumerate(doc['source_refs']):
 ref=b.source_ref(snap,e['source_ref'].split('@')[0]);path=b.ROOT/ref['path'];ck('exact-admitted-local-upstream-'+str(i),ref['version_ref']==e['source_ref'] and ref['sha256']==b.r.digest(path.read_bytes())==e['content_sha256'] and e['admission_posture']=='admitted' and e['source_admission_ref'] is not None);refs['upstream-'+str(i)]=b.ref(path);upstreams.append({'embedded_source_ref':e,'exact_local_ref':refs['upstream-'+str(i)],'whole_theory_imported':False})
ck('four-separate-local-upstreams',len(upstreams)==4)
ck('next-native-absent',not (b.BASE/'definitions/cal.definition.typed-connection-extension-rule').exists())
b.unchanged(list(refs.values()));ck('all-inputs-current',b.r.verify(snap,b.ROOT)['files']==201)
report={'schema_version':'definition-assurance-next-source-inspection/v1-candidate','authority_effect':'none','source':source,'source_units':len(b.co.inventory(doc)),'checks':checks,'selected_inputs':refs,'upstream_observations':upstreams,'projection_bytes':len(one),'projection_sha256':b.r.digest(one),'external_file_refs':[],'requires_ConstraintCycleSafety_full_delivery_audit_first':True,'actual_next_unit_created':False,'interpretation_or_models_created':False,'native_or_live_consumer_executed':False,'actual_endpoint_registration_connection_or_authority_created':False,'semantic_ready':False,'mechanized_proof':False}
if '--write' in sys.argv:
 with (P/'source-inspection.json').open('x') as out:json.dump(report,out,indent=2,sort_keys=True);out.write('\n')
else:assert b.r.same_json(report,json.loads((P/'source-inspection.json').read_bytes()))
print(json.dumps({'result':'PASS-next-TypedConnectionExtensionRule-source-only','checks':len(checks),'source_units':report['source_units'],'projection_bytes':len(one),'local_upstreams':len(upstreams),'actual_next_unit_created':False},indent=2))


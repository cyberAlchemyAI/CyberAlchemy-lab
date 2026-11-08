"""Exact C64 positive source/admission/projections/upstreams and source-query correspondence."""
from pathlib import Path
import json,sys,ast,copy
import build_candidate as b
def load(n):return json.loads((b.UNIT/n).read_bytes())
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();assert b.r.verify(snap,b.ROOT)['files']==201;source=b.source_ref(snap,'cal.definition.typed-connection-extension-rule');doc=b.co.source_document(snap,source);dp=b.ROOT/'docs/decisions/0064-typed-connection-extension-rule-admission/decision.json';decision=json.loads(dp.read_bytes());ap=dp.with_name('authorization.json');auth=json.loads(ap.read_bytes())
 paths={'source':b.ROOT/source['path'],'projection':(b.ROOT/source['path']).with_name('DEFINITION.md'),'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_snapshot':b.BASE/'current-snapshot.json','checker':b.UNIT/'verify_source_checks.py','C64_decision':dp,'C64_authorization':ap,'C64_candidate':b.ROOT/auth['candidate']['path'],'C64_validation':b.ROOT/auth['validation_receipt']['path']};refs={k:b.ref(v) for k,v in paths.items()};checks=[]
 def ck(n,ok):assert ok,n;checks.append({'check_id':n,'result':True})
 row=next(x for x in snap['current_entries'] if x['definition_id']==source['definition_id'])
 ck('exact-current-C64-source',source['sha256']==refs['source']['sha256']=='9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962' and row['effective_state']=='admitted-current' and row['admission_decision_ref']==decision['decision_id']=='CAL-DECISION-0064-TYPED-CONNECTION-EXTENSION-RULE-ADMISSION' and decision['status']=='owner-admitted')
 ck('original183189201scope',len(snap['current_entries'])==183 and len(snap['historical_entries'])==6)
 ck('C64-exact-selected-definition',all(decision['admitted_definition'][k]==source[k] for k in ['path','sha256']) and decision['admitted_definition']['definition_ref']==source['version_ref'])
 ck('C64-authorization-binding',refs['C64_authorization']['sha256']==decision['authorization']['sha256'] and auth['definition']=={'path':source['path'],'sha256':source['sha256']})
 ck('C64-candidate-binding',refs['C64_candidate']['sha256']==auth['candidate']['sha256']);ck('C64-validation-binding',refs['C64_validation']['sha256']==auth['validation_receipt']['sha256'])
 ck('C64-no-consumer-relation-or-pair-effects',decision['admission_result']['consumer_activations']==decision['admission_result']['relation_kinds_admitted']==decision['admission_result']['endpoint_pairs_admitted']==0)
 ck('Definition-schema-binding',doc['schema_digest']==refs['Definition_schema']['sha256']);ck('Definition-generator-binding',doc['source_direction']['generator_sha256']==refs['Definition_generator']['sha256']);ck('Definition-shape',not list(b.c.Draft202012Validator(json.loads(paths['Definition_schema'].read_bytes())).iter_errors(doc)))
 nodes=[x for x in ast.parse(paths['Definition_generator'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in ['esc','bullets','render']];ck('only-three-pure-functions',len(nodes)==3);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['Definition_generator']),'exec'),ns);before=copy.deepcopy(doc);one=ns['render'](doc).encode();two=ns['render'](doc).encode();ck('two-exact-projections-no-mutation',one==two==paths['projection'].read_bytes() and before==doc)
 f=doc['voices']['scientific_formal'];norm=f['normative_statement'];formal=f['formal_expression']
 ck('finite-closed-exact-ordered-genus','finite closed set of exact ordered source-kind to target-kind connections' in norm)
 ck('effective-predecessor-exact-successor',all(x in norm for x in ['effective predecessor Relation Kind version','exact successor contract version']))
 ck('pair-specific-qualifier-values-and-constraints','pair-specific values and constraints' in norm and 'PairQualifierSchema' in formal)
 ck('same-semantic-question-or-distinct-kind',all(x in norm for x in ['same unique semantic question','distinct Relation Kind']))
 ck('local-and-registration-not-global-pairs',all(x in formal for x in ['Local(o,s,t) does not imply','Register(k) does not imply']))
 ck('instance-conformance-admitted-effective-contract','exact contract is admitted and effective' in formal)
 ck('no-index-cartesian-wildcard-observation-inference',all(x in norm for x in ['endpoint registration','separate source and target lists','wildcard matching','historical observation','local graph use','candidate validation','second writable projection']))
 ck('exclusive-canonical-authority','{TypedRelation, SpecializedCarrier}' in formal and 'never both' in f['testable_conditions'][7])
 ck('nine-scientific-boundaries-twelve-tests',len(f['boundary_conditions'])==9 and len(f['testable_conditions'])==12)
 upstreams=[]
 for i,e in enumerate(doc['source_refs']):
  ref=b.source_ref(snap,e['source_ref'].split('@')[0]);path=b.ROOT/ref['path'];ck('exact-admitted-local-upstream-'+str(i),ref['version_ref']==e['source_ref'] and ref['sha256']==b.r.digest(path.read_bytes())==e['content_sha256'] and e['admission_posture']=='admitted' and e['source_admission_ref'] is not None);refs['upstream-'+str(i)]=b.ref(path);upstreams.append({'embedded_source_ref':e,'exact_local_ref':refs['upstream-'+str(i)],'whole_theory_imported':False})
 ck('four-upstream-meanings-kept-separate',len(upstreams)==4)
 ck('symbolic-consumer-routes-no-activation',doc['primary_consumer_refs']==['CAL-AXIS-ORTHOGONAL-RELATION-MODEL-0002','cal.artifact-type.relation-kind/successor'])
 core=load('t.json')['payload'];counts=load('denominator.json');ck('native61units61mapped43encoded16explanatory2deferred',core['source']==source and counts['source_units']==counts['mapped_clauses']==61 and counts['encoded_clauses']==43 and counts['explanatory_clauses']==16 and counts['deferred_clauses']==2)
 texts=dict(b.co.string_leaves(doc));queries={x['query_id'] for x in load('query-policy.json')['queries']}
 for i,x in enumerate(load('source-query-obligation.json')['obligations']):
  clause=next(y for y in core['clauses'] if y['clause_id']==x['clause_id']);excerpt=texts[x['selector']][x['start_character']:x['end_character']];ck('source-query-obligation-'+str(i),x['source']==source and excerpt==x['excerpt'] and b.r.digest(excerpt.encode())==x['excerpt_sha256']==clause['excerpt_sha256'] and x['start_character']==clause['start_character'] and x['query_id'] in queries and x['selected_in_T'] is False and x['actual_outcome_target_in_T'] is False and x['necessary_declaration_guard_in_T']==(clause['disposition']=='encoded'))
 report={'schema_version':'definition-assurance-TypedConnectionExtension-source-checks/v1-candidate','status':'PASS-exact-current-C64-TypedConnectionExtension-and-four-upstreams','authority_effect':'none','source':source,'selected_inputs':refs,'checks':checks,'first_render_sha256':b.r.digest(one),'second_render_sha256':b.r.digest(two),'projection_bytes':len(one),'current_registry_admission_ref':row['admission_decision_ref'],'recorded_local_source_observations':upstreams,'recorded_consumer_routes':[{'label':x,'accepted_operational_map':False,'consumer_activated':False} for x in doc['primary_consumer_refs']],'external_file_refs':[],'native_or_live_consumer_executed':False,'actual_endpoint_registration_connection_or_authority_created':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'source_precedence':'Twenty-three Typed Connection Extension findings unresolved','claim_ceiling':'Exact C64 source/admission/currentness,pure projections,four local upstreams and source-query correspondence only;actual endpoint/contract resolution,admission,qualifier validity,conformance,global availability,authority and whole proof pending.'}
 b.unchanged(list(refs.values())+context['sources']);b.external_current(context)
 if write:
  b.put('source-checks.json',report)
  for n,raw in [('source-render-1.md',one),('source-render-2.md',two)]:
   with (b.UNIT/n).open('xb') as f:f.write(raw)
 elif not b.r.same_json(report,load('source-checks.json')) or one!=(b.UNIT/'source-render-1.md').read_bytes() or two!=(b.UNIT/'source-render-2.md').read_bytes():raise ValueError('Fresh Typed Connection Extension source observations differ')
 return report
def main():
 x=verify('--write' in sys.argv);print(json.dumps({'result':x['status'],'checks':len(x['checks']),'projection_bytes':x['projection_bytes'],'projection_sha256':x['first_render_sha256'],'local_upstreams':len(x['recorded_local_source_observations'])},indent=2))
if __name__=='__main__':main()


"""Exact C28 Semantic Epoch source, pure projections and native query correspondence."""
from pathlib import Path
import sys,json,ast,copy
import build_candidate as b
def load(n):return json.loads((b.UNIT/n).read_bytes())
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context)
 snap=b.snapshot();assert b.r.verify(snap,b.ROOT)['files']==201;source=b.source_ref(snap,'cal.definition.semantic-epoch');doc=b.co.source_document(snap,source)
 decision_path=b.ROOT/'docs/decisions/0028-craft-foundation-v1/decision.json';decision=json.loads(decision_path.read_bytes());auth_path=decision_path.with_name('authorization.json');auth=json.loads(auth_path.read_bytes());manifest_path=b.ROOT/auth['manifest']['path'];manifest=json.loads(manifest_path.read_bytes())
 paths={'source':b.ROOT/source['path'],'projection':(b.ROOT/source['path']).with_name('DEFINITION.md'),'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_snapshot':b.BASE/'current-snapshot.json','checker':b.UNIT/'verify_source_checks.py','C28_decision':decision_path,'C28_authorization':auth_path,'C28_manifest':manifest_path,'C28_validation':b.ROOT/auth['validation_receipt']['path']}
 refs={k:b.ref(q) for k,q in paths.items()};checks=[]
 def ck(n,ok):
  assert ok,n;checks.append({'check_id':n,'result':True})
 row=next(x for x in snap['current_entries'] if x['definition_id']==source['definition_id']);ck('exact-current-source',source['version_ref']=='cal.definition.semantic-epoch@1.0.0-candidate.1' and source['sha256']==refs['source']['sha256']=='e138c57bf7a69f958ca966690428bde166ff9d2137f557a14e153e94028272e3')
 ck('C28-current-overlay',row['effective_state']=='admitted-current' and row['admission_decision_ref']==decision['decision_id']=='CAL-DECISION-0028-CRAFT-FOUNDATION-V1' and decision['status']=='owner-admitted')
 ck('original-scope',len(snap['current_entries'])==183 and len(snap['current_entries'])+len(snap['historical_entries'])==189 and len(snap['captured_files'])==201)
 ck('C28-exact-selected-definition',any(x['definition_id']==source['definition_id'] and x['path']==source['path'] and x['sha256']==source['sha256'] for x in decision['admitted_definitions']))
 ck('C28-exact-manifest',refs['C28_manifest']['sha256']==auth['manifest']['sha256']==decision['selection']['manifest_sha256'])
 ck('C28-exact-validation-bytes',refs['C28_validation']['sha256']==auth['validation_receipt']['sha256']==decision['selection']['validation_receipt_sha256'])
 ck('C28-authorization-token',auth['status']=='exact-owner-authorized' and auth['selection_token']==decision['selection']['selection_token'])
 ck('C28-no-implementation-binding',decision['admission_result']['implementation_bindings_accepted']==0)
 schema=json.loads(paths['Definition_schema'].read_bytes());ck('Definition-schema-binding',doc['schema_digest']==refs['Definition_schema']['sha256']);ck('Definition-generator-binding',doc['source_direction']['generator_sha256']==refs['Definition_generator']['sha256']);ck('Definition-shape',not list(b.c.Draft202012Validator(schema).iter_errors(doc)))
 nodes=[x for x in ast.parse(paths['Definition_generator'].read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in ['esc','bullets','render']];ck('pure-functions-only',len(nodes)==3);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(paths['Definition_generator']),'exec'),ns);before=copy.deepcopy(doc);one=ns['render'](doc).encode();two=ns['render'](doc).encode();ck('two-exact-projections-and-no-mutation',one==two==paths['projection'].read_bytes() and before==doc)
 f=doc['voices']['scientific_formal'];expr=f['formal_expression'];norm=f['normative_statement']
 ck('immutable-owner-selected-meaning-genus',all(x in norm for x in ['one immutable owner-selected version',"artifact's normative meaning"]))
 ck('successor-owner-determines-material-change',all(x in norm for x in ['successor Semantic Epoch is required exactly when','owner determines','identity-preserving normative meaning, scope, exclusions, owned model, or semantic contracts materially changed']))
 ck('representation-and-derived-refresh-do-not-create-epochs','Representation-only revisions and derived refreshes do not create Semantic Epochs.' in norm)
 ck('formal-material-meaning-iff', 'NewSemanticEpoch(a_before,a_after) iff MaterialNormativeMeaning(a_before) != MaterialNormativeMeaning(a_after)' in expr)
 ck('representation-change-not-sufficient','RepresentationChanged and MeaningEqual does not imply NewSemanticEpoch.' in expr)
 ck('byte-label-and-equivalence-boundaries',all(x in f['boundary_conditions'] for x in ['A byte change alone does not prove semantic change.','A claim that meaning is preserved is reviewable evidence, not automatic equivalence.','A semantic successor requires explicit owner selection and applicable lineage.']))
 ck('three-exclusions-three-boundaries-three-tests-two-notations',len(doc['scope']['exclusions'])==3 and len(doc['boundaries'])==3 and len(f['testable_conditions'])==3 and len(f['notation'])==2)
 ck('positive-predecessor-delta-and-negative-representation-tests',all(x in f['testable_conditions'] for x in ['The change assessment separates semantic fields from representation fields.','Every new epoch identifies its predecessor and material meaning delta.','No representation-only change is classified as semantic lineage.']))
 ck('source-body-does-not-select-existing-successor','does not classify any existing artifact, create lineage, or select a successor' in doc['claim_ceiling'])
 observations=[]
 for i,x in enumerate(doc['source_refs']):
  row=next(z for z in snap['current_entries']+snap['historical_entries'] if z['version_ref']==x['source_ref']);r={k:row[k] for k in ['definition_id','version_ref','path','sha256']};q=b.ROOT/r['path'];paths['upstream-'+str(i)]=q;refs['upstream-'+str(i)]=b.ref(q);observations.append({'embedded_source_ref':x,'current_or_historical_exact_ref':r,'accepted_semantic_map':False});assert r['sha256']==x['content_sha256']==refs['upstream-'+str(i)]['sha256']
 ck('two-exact-local-upstream-sources',len(observations)==2 and {x['embedded_source_ref']['source_ref'] for x in observations}=={'cal.definition.definition@1.0.0-candidate.1','cal.definition.bounded-context@2.0.0-candidate.1'})

 ck('native-exact-source-and26units',load('t.json')['payload']['source']==source and len(b.co.inventory(doc))==26)
 core=load('t.json')['payload'];texts=dict(b.co.string_leaves(doc));queries={x['query_id'] for x in load('query-policy.json')['queries']};obligations=load('source-query-obligation.json')['obligations']
 for i,x in enumerate(obligations):
  clause=next(y for y in core['clauses'] if y['clause_id']==x['clause_id']);excerpt=texts[x['selector']][x['start_character']:x['end_character']];ck('source-query-obligation-'+str(i),x['source']==source and excerpt==x['excerpt'] and b.r.digest(excerpt.encode())==x['excerpt_sha256']==clause['excerpt_sha256'] and x['query_id'] in queries and x['selected_in_T'] is False and x['actual_outcome_target_in_T'] is False and x['necessary_declaration_guard_in_T']==(clause['disposition']=='encoded'))
 report={'schema_version':'definition-assurance-SemanticEpoch-source-checks/v1-candidate','status':'PASS-exact-current-C28-SemanticEpoch-and-local-upstreams','authority_effect':'none','source':source,'selected_inputs':refs,'checks':checks,'first_render_sha256':b.r.digest(one),'second_render_sha256':b.r.digest(two),'projection_bytes':len(one),'current_registry_admission_ref':row['admission_decision_ref'],'recorded_local_source_observations':observations,'all_local_upstream_source_bytes_verified':True,'external_file_refs':[],'native_or_live_consumer_executed':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'source_precedence':'Twenty-two Semantic Epoch findings unresolved','claim_ceiling':'Exact C28 source/currentness,pure Definition projections and source/query correspondence only;no actual meaning difference,owner selection,lineage,immutable storage,effect authority or whole proof.'}
 b.unchanged(list(refs.values())+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if write:
  b.put('source-checks.json',report)
  for n,raw in [('source-render-1.md',one),('source-render-2.md',two)]:
   with (b.UNIT/n).open('xb') as f:f.write(raw)
 elif not b.r.same_json(report,load('source-checks.json')) or one!=(b.UNIT/'source-render-1.md').read_bytes() or two!=(b.UNIT/'source-render-2.md').read_bytes():raise ValueError('Fresh Semantic Epoch source observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'checks':len(x['checks']),'projection_bytes':x['projection_bytes'],'projection_sha256':x['first_render_sha256'],'local_upstreams':len(x['recorded_local_source_observations'])},indent=2))
if __name__=='__main__':main()

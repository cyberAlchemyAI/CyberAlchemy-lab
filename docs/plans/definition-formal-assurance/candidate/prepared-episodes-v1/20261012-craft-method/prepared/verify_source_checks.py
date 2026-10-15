"""Fresh exact C29 Craft source,projection,scoped upstream and source-query checks."""
from pathlib import Path
import json,sys,ast,copy
import build_candidate as b
def load(n):return json.loads((b.UNIT/n).read_bytes())
def verify(write=False):
 context=load("context.json");b.unchanged(context["sources"]);b.external_current(context)
 snap=b.snapshot();source=b.source_ref(snap,'CAV2-D20');doc=b.co.source_document(snap,source);dp=b.ROOT/'docs/decisions/0029-cml07-semantic-foundation-v1/decision.json';decision=json.loads(dp.read_bytes());ap=dp.with_name('authorization.json');auth=json.loads(ap.read_bytes())
 paths={'source':b.ROOT/source['path'],'projection':(b.ROOT/source['path']).with_name('DEFINITION.md'),'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','current_snapshot':b.BASE/'current-snapshot.json','checker':b.UNIT/'verify_source_checks.py','C29_decision':dp,'C29_authorization':ap,'C29_manifest':b.ROOT/auth['manifest']['path'],'C29_validation':b.ROOT/auth['validation_receipt']['path'],'C29_Craft_candidate':b.ROOT/decision['admitted_definition_candidates'][0]['path'],'C29_selected_chain':b.ROOT/decision['selected_chain']['path']}
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
  else:up.append({'embedded_source_ref':e,'external_bytes_read':True,'external_currentness':'exact-selected-scope-checked','whole_theory_imported':False})
 ck('three-distinct-upstream-references',len(up)==3)
 ck('body-historical-chain-evidence-retained','CAL-CML07-CRAFT-IDENTITY-CHAIN-0001' in doc['evidence_refs'] and decision['selected_chain']['chain_id']=='CAL-CML07-CRAFT-IDENTITY-CHAIN-0002')
 ck('method-binding-consumer-routes-kept-separate',doc['primary_consumer_refs']==['authority/artifact-types/method-binding/v1','product/products/craft/v1/method-binding.json'])

 admissions_path=b.ROOT/'authority/decisions/source-admission/craft-identity-v1/v1/admissions.json';admissions=json.loads(admissions_path.read_bytes());refs['source_admissions']=b.ref(admissions_path)
 request=next(x for x in decision['admitted_decision_requests'] if x['request_id']=='CML07-DR-01-SOURCE-IDENTITY')
 ck('C29-eight-distinct-owner-requests',len(decision['admitted_decision_requests'])==8 and request['target_path']==refs['source_admissions']['path'] and len(admissions['admissions'])==8)
 ck('body-candidate-posture-retained-with-current-scoped-admission',admissions['status']=='candidate-unadmitted' and admissions['authority_effect']=='none-until-bound-decision' and all(x['admission_posture']=='candidate-unadmitted' and x['source_admission_ref'] is None for x in doc['source_refs'][1:]))
 ck('C29-eleven-source-admissions-positive',decision['admission_result']['source_selections_admitted']==11)
 md=b.ROOT.parent/'cyberAlchemy-v2/authority/definitions/DEFINITIONS.md';original=b.ROOT.parent/'domainspec-core/cyberAlchemy-v2/authority/definitions/DEFINITIONS.md';product=b.ROOT.parent/'domainspec-core/cyberAlchemy-v2/product/craft/IDENTITY.json'
 entries=[next(x for x in admissions['admissions'] if x['admission_id']==n) for n in ['CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-CAV2-D20','CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-PRODUCT']]
 selected=b''.join(md.read_bytes().splitlines(keepends=True)[1013:1185]);mdhash=b.r.digest(md.read_bytes());producthash=b.r.digest(product.read_bytes())
 ck('relocated-exact-lines1014-1185',not original.exists() and entries[0]['start_line']==1014 and entries[0]['end_line']==1185 and b.r.digest(selected)==entries[0]['selected_sha256']==doc['source_refs'][1]['content_sha256'])
 ck('fullfile-drift-distinct-from-selected-scope',mdhash!=entries[0]['source_file_sha256_at_authoring'])
 ck('exact-product-wholefile',producthash==entries[1]['selected_sha256']==doc['source_refs'][2]['content_sha256'])
 ck('selected-Craft-target-uses',all('CAV2-D20' in x['target_definition_ids'] for x in entries) and 'Method binding' in entries[0]['target_use'])
 external=[{'absolute_path':str(md),'sha256':mdhash,'original_declared_absolute_path':str(original),'original_path_present':False,'relocation_observed':True,'selector':'lines:1014-1185','selected_sha256':b.r.digest(selected),'selected_bytes':len(selected),'historical_whole_file_sha256':entries[0]['source_file_sha256_at_authoring'],'authority_effect':'none'},{'absolute_path':str(product),'sha256':producthash,'selector':'whole-file','selected_sha256':producthash,'authority_effect':'none'}]
 for observation,entry,ext in zip(up[1:],entries,external):observation.update(source_admission_entry_id=entry['admission_id'],current_scoped_overlay_decision=decision['decision_id'],external_observation=ext)
 core=load('t.json')['payload'];counts=load('denominator.json');ck('native25mapped14encoded9expl2deferred',core['source']==source and counts['source_units']==counts['mapped_clauses']==25 and counts['encoded_clauses']==14 and counts['explanatory_clauses']==9 and counts['deferred_clauses']==2)
 texts=dict(b.co.string_leaves(doc));queries={x['query_id'] for x in load('query-policy.json')['queries']}
 for i,x in enumerate(load('source-query-obligation.json')['obligations']):
  clause=next(y for y in core['clauses'] if y['clause_id']==x['clause_id']);excerpt=texts[x['selector']][x['start_character']:x['end_character']];ck('source-query-obligation-'+str(i),x['source']==source and excerpt==x['excerpt'] and b.r.digest(excerpt.encode())==x['excerpt_sha256']==clause['excerpt_sha256'] and x['start_character']==clause['start_character'] and x['query_id'] in queries and x['selected_in_T'] is False and x['actual_outcome_target_in_T'] is False and x['necessary_declaration_guard_in_T']==(clause['disposition']=='encoded'))
 b.unchanged(list(refs.values())+context['sources']);b.external_current(context);ck('all-source201files-current',b.r.verify(snap,b.ROOT)['files']==201)
 report={'schema_version':'definition-assurance-CraftMethod-source-checks/v1-candidate','status':'PASS-exact-current-C29-CraftMethod-and-scoped-upstreams','authority_effect':'none','source':source,'selected_inputs':refs,'checks':checks,'first_render_sha256':b.r.digest(one),'second_render_sha256':b.r.digest(two),'projection_bytes':len(one),'current_registry_admission_ref':row['admission_decision_ref'],'recorded_local_source_observations':up,'recorded_consumer_routes':[{'label':x,'accepted_operational_map':False,'consumer_activated':False} for x in doc['primary_consumer_refs']],'external_file_refs':external,'native_or_live_consumer_executed':False,'actual_recursive_construction_closure_or_authority_created':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'source_precedence':'Twenty-two Craft Method source-owner findings unresolved','claim_ceiling':'Exact C29 source,currentness,pure projections,local upstream,relocated selected line-range,Product wholefile and source-query correspondence only;actual construction,conformance,determinism,closure,owner authority,source fidelity and whole proof pending.'}
 if write:
  b.put('source-checks.json',report)
  for n,raw in [('source-render-1.md',one),('source-render-2.md',two)]:
   with (b.UNIT/n).open('xb') as f:f.write(raw)
 elif not b.r.same_json(report,load('source-checks.json')) or one!=(b.UNIT/'source-render-1.md').read_bytes() or two!=(b.UNIT/'source-render-2.md').read_bytes():raise ValueError('Fresh Craft Method source observations differ')
 return report
def main():
 x=verify('--write' in sys.argv);print(json.dumps({'result':x['status'],'checks':len(x['checks']),'projection_bytes':x['projection_bytes'],'projection_sha256':x['first_render_sha256'],'upstreams':len(x['recorded_local_source_observations']),'external_scopes':len(x['external_file_refs'])},indent=2))
if __name__=='__main__':main()

"""Read exact next Registry source; do not create a native Registry interpretation."""
from pathlib import Path
import sys,json,ast,copy
U=Path(__file__).resolve().parents[1];sys.path.insert(0,str(U));import build_candidate as b

def main():
 context=json.loads((U/'context.json').read_bytes());typed=json.loads((U/'types-logic-receipt.json').read_bytes());prior=json.loads((U.parent/'cal.definition.artifact-lifetime/delivery-manifest.json').read_bytes());b.unchanged(context['sources']+typed['inputs']+prior['files']);b.external_current(context);snap=b.snapshot();live=b.r.verify(snap,b.ROOT);source=b.source_ref(snap,'cal.definition.artifact-type-registry');doc=b.co.source_document(snap,source);path=b.ROOT/source['path'];generator=b.ROOT/'authority/artifact-types/definition/v1/generator.py';schema=b.ROOT/'authority/artifact-types/definition/v1/schema.json';row=next(x for x in snap['current_entries'] if x['definition_id']==source['definition_id']);selected={'source':b.ref(path),'projection':b.ref(path.with_name('DEFINITION.md')),'generator':b.ref(generator),'schema':b.ref(schema),'snapshot':b.ref(b.BASE/'current-snapshot.json'),'definitions_registry':b.ref(b.ROOT/'authority/definitions/registry.json')};checks=[]
 def ck(n,ok):
  if not ok:raise ValueError(n)
  checks.append({'check_id':n,'result':True})
 ck('source-exact-current',source['sha256']=='e554069c42d0ee17d4df65a0de2b0bba998933622aa9aba296671a01dd273e81' and source['version_ref']=='cal.definition.artifact-type-registry@1.0.0-candidate.1' and selected['source']=={'path':source['path'],'sha256':source['sha256']})
 ck('source-admitted-current-C53',row['effective_state']=='admitted-current' and row['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
 ck('current-scope-preserved',len(snap['current_entries'])==183 and len(snap['historical_entries'])==6 and live['files']==201)
 validator=b.c.Draft202012Validator(json.loads(schema.read_bytes()));ck('Definition-shape',not list(validator.iter_errors(doc)))
 nodes=[n for n in ast.parse(generator.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name in ['esc','bullets','render']];ck('pure-render-functions-selected',len(nodes)==3);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(generator),'exec'),ns);before=copy.deepcopy(doc);first=ns['render'](before).encode();second=ns['render'](before).encode();ck('two-pure-projections-input-preserved',first==second==path.with_name('DEFINITION.md').read_bytes() and before==doc)
 formal=doc['voices']['scientific_formal'];ck('reference-index-not-admission',all(x in formal['normative_statement'] for x in ['canonical reference index','immutable Artifact Type contracts','does not redefine or admit']))
 ck('decision-overlay-currentness-distinct',all(x in formal['formal_expression'] for x in ['artifact@digest','schema@digest','discriminator','definitions','decision','state','registered_R(t) =/=> admitted(t)','only by exact owner decision overlay']))
 ck('at-most-one-current-discriminator',formal['testable_conditions'][1]=='Every instance discriminator resolves to at most one admitted current type.')
 ck('history-and-shared-selectors-retained',formal['boundary_conditions'][1]=='Historical admitted versions remain visible when a successor becomes current.' and formal['boundary_conditions'][2]=='Shared bootstrap schema selectors are valid exact bindings and need not be moved.')
 ck('primary-consumer-labels-retained',doc['primary_consumer_refs']==['cal.artifact-type.artifact-type-registry/v1','cal.definition.artifact-type-resolution@1.0.0-candidate.1'])
 observations=[]
 for ref in doc['source_refs']:
  candidates=[x for x in snap['current_entries']+snap['historical_entries'] if x['version_ref']==ref['source_ref']];ck('exact-upstream-'+ref['source_ref'],len(candidates)==1 and candidates[0]['sha256']==ref['content_sha256']);q=candidates[0];selected[q['version_ref']]=b.ref(b.ROOT/q['path']);ck('local-upstream-bytes-'+q['version_ref'],selected[q['version_ref']]['sha256']==q['sha256']);observations.append({'source_ref':q['version_ref'],'sha256':q['sha256'],'effective_state':q['effective_state']})
 next_unit=U.parent/'cal.definition.artifact-type-registry';ck('next-native-unit-absent',not next_unit.exists());b.unchanged(list(selected.values())+typed['inputs']+prior['files']);b.external_current(context)
 result={'schema_version':'definition-assurance-next-source-inspection/v1-candidate','authority_effect':'none','source':source,'status':'PASS-for-exact-Registry-source-only','checks':checks,'source_units':len(b.co.inventory(doc)),'projection_bytes':len(first),'projection_sha256':b.r.digest(first),'selected_inputs':selected,'upstream_observations':observations,'requires_Surface_full_delivery_audit_first':True,'actual_next_unit_created':False,'interpretation_or_models_created':False,'native_or_live_consumer_executed':False,'semantic_ready':False,'mechanized_proof':False,'source_fidelity':'pending','owner_acceptance_ref':None}
 with (Path(__file__).parent/'source-inspection.json').open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
 print(json.dumps({'result':result['status'],'checks':len(checks),'source_units':result['source_units'],'projection_bytes':len(first),'native_unit_created':False},indent=2))
if __name__=='__main__':main()

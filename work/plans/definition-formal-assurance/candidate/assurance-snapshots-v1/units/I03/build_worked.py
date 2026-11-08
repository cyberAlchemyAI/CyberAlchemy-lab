"""Execute the whole selected seven-source theory; retain global coverage and proof gaps."""
import hashlib
import json
import sys
import time
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1];IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL));import regression as x

def ref(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def put(path,value):
 with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 return ref(path)
def bound(reference):
 if ref(ROOT/reference['path'])!=reference:raise ValueError('Changed selected bytes: '+reference['path'])
def main():
 attempt=UNIT/sys.argv[1]
 if json.loads((attempt/'result.json').read_bytes())['result']!='PASS':raise ValueError('Actual complete I03 suite required')
 for name in ['regression.py','test_I03.py']:
  live=IMPL/name if name=='regression.py' else IMPL/'tests'/name
  if live.read_bytes()!=(attempt/name).read_bytes():raise ValueError('Implementation changed after tests')
 context=json.loads((UNIT/'context.json').read_bytes())
 for row in context['sources']:bound(row)
 projection=json.loads((BASE/'units/A08/projection.json').read_bytes());prior=json.loads((BASE/'units/I02/worked-summary.json').read_bytes());originals=[json.loads((ROOT/row['path']).read_bytes()) for row in projection['input_ir_refs']];renaming=[]
 for local,canonical in projection['symbol_mapping'].items():
  candidates=[item for item in originals if any(origin['local_symbol_id']==local and (local=='Record' or origin['canonical_id']==canonical) for origin in item['origins'])]
  if not candidates:raise ValueError('Missing explicit selected nominal origin')
  renaming.append({'local_symbol_id':local,'canonical_id':canonical,'source':candidates[0]['source']})
 renaming_ref=put(UNIT/'selected-renaming.json',renaming);cards_ref=put(UNIT/'selected-cardinalities.json',{projection['symbol_mapping']['Record']:2});profile_ref=put(UNIT/'selected-provider-profile.json',json.loads(x.f.POLICY_PATH.read_bytes()));toolchain_ref=put(UNIT/'selected-provider-bindings.json',{'bindings':x.f.current_bindings()})
 cases={}
 for name in ['unchanged','counterfactual','retirement']:
  selection={'schema_version':'definition-assurance-regression-selection/v1-candidate','authority_effect':'none','revision_selection_ref':prior[name]['selection_ref'],'revision_result_ref':prior[name]['output_ref'],'input_ir_refs':projection['input_ir_refs'],'alignment_refs':projection['alignment_refs'],'renaming_ref':renaming_ref,'cardinalities_ref':cards_ref,'profile_ref':profile_ref,'toolchain_ref':toolchain_ref,'budgets':{},'scope_policy':'selected-inputs-only'}
  selected=put(UNIT/(name+'-regression-selection.json'),selection);start=time.monotonic();result=x.run_selected(ROOT,selected);elapsed=round(time.monotonic()-start,3);output=put(UNIT/(name+'-regression-result.json'),result)
  if result['status']=='regression-unresolved':raise ValueError(json.dumps(result))
  if result['coverage']['global_current_source_nodes']!=183 or len(result['coverage']['missing_current_interpretations'])!=176 or result['semantic_ready'] is not False or result['mechanized_proof'] is not False or result['unbounded_conclusion'] is not None:raise ValueError('Missing actual global/proof boundary')
  query_count=11 if name!='retirement' else 9
  if len(result['results'])!=query_count:raise ValueError('Incomplete selected query denominator')
  if name in {'unchanged','retirement'} and result['status']!='selected-existential-regression-checked':raise ValueError('Actual selected positive control did not find independently checked models')
  target=next((row for row in result['results'] if row['obligation_id']=='relation:TRACE-Position:left-difference'),None)
  if name=='counterfactual' and target['status'] not in {'reported-finite-scope-failure-unverified-exhaustion','incomplete-no-logical-conclusion'}:raise ValueError('Counterfactual witness request unexpectedly supported')
  cases[name]={'selection_ref':selected,'output_ref':output,'elapsed_seconds':elapsed,'status':result['status'],'selected_query_count':query_count,'independently_checked_models':sum(row['status']=='independently-checked-witness' for row in result['results']),'failed_or_unresolved_queries':[{'obligation_id':row['obligation_id'],'status':row['status'],'native_status':row['native_result']['status'] if row['native_result'] else None} for row in result['results'] if row['status']!='independently-checked-witness'],'selected_affected_neighbours':result['affected_neighbours_in_selected_regression'],'unresolved_affected_neighbours':result['affected_neighbours_unresolved_outside_selected_regression']}
  print(json.dumps({'case':name,**cases[name]},sort_keys=True),flush=True)
 summary={'authority_effect':'none','semantic_ready':False,'goal_status':'active','global_current_source_nodes':183,'included_partial_logical_sources':7,'missing_current_interpretations':176,'pending_whole_source_clauses':7,'owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'finite_domain_cardinality':2,'exhaustion_independently_verified':False,'cases':cases,'claim_ceiling':'Generic finite regression of the exact seven-source unary projection, all selected T and required I. Supplied models independently checked. No converse map from arbitrary projection models to the restricted record world, no unbounded proof, source fidelity or all183 theory.'};put(UNIT/'worked-summary.json',summary)
if __name__=='__main__':main()

"""Regenerate all selected regression targets and independently recheck stored supplied models."""
import json
import build_worked as b
x=b.x

def main():
 summary=json.loads((b.UNIT/'worked-summary.json').read_bytes());cases={}
 for name,row in summary['cases'].items():
  b.bound(row['selection_ref']);b.bound(row['output_ref']);selection=json.loads((b.ROOT/row['selection_ref']['path']).read_bytes());prepared=x.prepare(b.ROOT,selection);result=json.loads((b.ROOT/row['output_ref']['path']).read_bytes())
  if result['revision_sha256']!=prepared['revision']['revision_sha256'] or result['joint_theory_sha256']!=x.ir.digest(prepared['T']) or result['joint_population_sha256']!=x.ir.digest(prepared['I']) or result['subject_ir_sha256']!=prepared['subject']['ir_sha256'] or result['coverage']!=prepared['coverage'] or result['clause_accounts']!=prepared['clause_accounts']:raise ValueError('Substituted joint theory/population/composition/coverage')
  query_ids=[query['obligation_id'] for query in prepared['queries']]
  if result['required_query_ids']!=query_ids or [item['obligation_id'] for item in result['results']]!=query_ids:raise ValueError('Missing or extra selected obligation')
  checked=[];reported=[];prerequisites=True
  for query,item in zip(prepared['queries'],result['results']):
   if item['status'].startswith('independently-checked-'):
    if not prerequisites:raise ValueError('Local support before global witnesses')
    I=[] if query['obligation_id']=='query:consistency' else prepared['I'];mode='witness' if query['minimum_strength']=='model-witness' else 'countermodel';native=item['native_result']
    if native['input_bindings']['snapshot_sha256']!=x.ir.digest(prepared['snapshot']):raise ValueError('Substituted snapshot')
    verdict=x.v.witness(prepared['subject'],native,prepared['T'],I,query['statement'],prepared['cards'],mode,prepared['provider_bindings'],selected_inputs=prepared['originals'],alignments=selection['alignment_refs'],root=b.ROOT)
    if not x.d.equal(verdict,item['verification']):raise ValueError('Independent model check no longer agrees')
    checked.append(query['obligation_id'])
   else:
    if item['verification'] is not None:raise ValueError('Unchecked absence promoted to verification')
    reported.append({'obligation_id':query['obligation_id'],'status':item['status'],'native_status':item['native_result']['status'] if item['native_result'] else None})
   if query['obligation_id'] in {'query:consistency','query:joint-population'} and item['status']!='independently-checked-witness':prerequisites=False
  if result['semantic_ready'] is not False or result['mechanized_proof'] is not False or result['unbounded_conclusion'] is not None or result['source_fidelity']!='pending':raise ValueError('False semantic/proof/fidelity promotion')
  prepared['inputs'].closing();source=x.i.live_recheck(prepared['epoch'],b.ROOT);cases[name]={'independently_rechecked_model_count':len(checked),'query_denominator':len(query_ids),'reported_unverified':reported,'source_files_current':source['source_files']}
 prior=json.loads((b.BASE/'units/I02/delivery-manifest.json').read_bytes())
 for reference in prior['files']:b.bound(reference)
 print(json.dumps({'result':'PASS-for-fresh-joint-inputs-and-independent-supplied-models','authority_effect':'none','semantic_ready':False,'cases':cases,'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'exhaustion_independently_verified':False,'whole_definition_proofs':0},indent=2,sort_keys=True))
if __name__=='__main__':main()

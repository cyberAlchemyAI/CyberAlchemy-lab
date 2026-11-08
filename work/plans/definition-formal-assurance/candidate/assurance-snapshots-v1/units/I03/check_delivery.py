"""Read-only I03 receipt, implementation and preserved-delivery byte audit."""
import json
import build_worked as b

def main():
 receipt=json.loads((b.UNIT/'receipt.json').read_bytes());manifest=json.loads((b.UNIT/'delivery-manifest.json').read_bytes());prior=json.loads((b.BASE/'units/I02/delivery-manifest.json').read_bytes())
 for reference in receipt['inputs']+receipt['outputs']+manifest['files']+prior['files']:b.bound(reference)
 for name in ['I02','P02']:
  earlier=json.loads((b.BASE/f'units/{name}/receipt.json').read_bytes())
  for reference in earlier['inputs']+earlier['outputs']:b.bound(reference)
 source=b.x.i.live_recheck(b.x.i.read_epoch(b.ROOT,b.ref(b.BASE/'units/I01/current-epoch.json')),b.ROOT)
 if receipt['semantic_ready'] is not False or receipt['full_project_completion']!='not-established' or receipt['validation']['test_count']!=29 or receipt['validation']['test_result']!='PASS' or source['source_files']!=201:raise ValueError('False readiness or invalid denominator')
 print(json.dumps({'result':'PASS','candidate_files':len(manifest['files']),'prior_candidate_files_preserved':len(prior['files']),'source_files_current':201,'I03_tests':29,'semantic_ready':False,'whole_definition_proofs':0,'goal_status':'active','next_ready_unit':'I04.1'},indent=2,sort_keys=True))
if __name__=='__main__':main()

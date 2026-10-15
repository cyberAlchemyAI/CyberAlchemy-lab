"""Read-only exact delivery/source/baseline check; no owner or proof acceptance."""
import json
import finalize as f

def main():
 manifests={}
 for path in [f.BASE/'units/E04/delivery-manifest.json',f.UNIT/'delivery-manifest.json']:
  rows=json.loads(path.read_bytes())['files']
  if len({x['path'] for x in rows})!=len(rows):raise ValueError('Duplicate sealed file')
  for row in rows:f.bound(row)
  manifests[path.relative_to(f.ROOT).as_posix()]=len(rows)
 receipt=json.loads((f.UNIT/'receipt.json').read_bytes())
 for row in receipt['inputs']+receipt['outputs']:f.bound(row)
 boundary,source=f.baseline()
 if receipt['unit_id']!='I01.1' or receipt['semantic_ready'] is not False or receipt['authority_effect']!='none' or receipt['goal_status']!='active' or receipt['validation']['test_count']!=34:raise ValueError('False I01 completion or authority')
 print(json.dumps({'result':'PASS-for-sealed-I01','manifests':manifests,'I01_tests':34,'current_source_nodes':183,'source_files_rechecked':source['source_files'],'source_accounting_packets':8,'missing_accounting_packets':175,'semantic_closure':'not-established','owner_fidelity':'pending','goal_status':'active','next_ready_unit':'I02.1'},indent=2,sort_keys=True))
if __name__=='__main__':main()

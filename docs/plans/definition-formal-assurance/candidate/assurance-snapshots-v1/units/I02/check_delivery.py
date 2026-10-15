"""Verify sealed current/prior revision artifacts; never derive authority or proof acceptance."""
import json
import finalize as f

def main():
 manifests={}
 for path in [f.BASE/'units/I01/delivery-manifest.json',f.UNIT/'delivery-manifest.json']:
  rows=json.loads(path.read_bytes())['files']
  if len({x['path'] for x in rows})!=len(rows):raise ValueError('Duplicate delivery identity')
  for row in rows:f.bound(row)
  manifests[path.relative_to(f.ROOT).as_posix()]=len(rows)
 receipt=json.loads((f.UNIT/'receipt.json').read_bytes())
 for row in receipt['inputs']+receipt['outputs']:f.bound(row)
 if receipt['unit_id']!='I02.1' or receipt['goal_status']!='active' or receipt['semantic_ready'] is not False or receipt['evidence_verified'] is not False or receipt['validation']['test_count']!=33:raise ValueError('False completion or proof acceptance')
 epoch=f.b.d.i.read_epoch(f.ROOT,f.ref(f.BASE/'units/I01/current-epoch.json'));source=f.b.d.i.live_recheck(epoch,f.ROOT)
 print(json.dumps({'result':'PASS-for-sealed-I02','manifests':manifests,'I02_tests':33,'fresh_worked_controls':3,'current_source_nodes':len(epoch['nodes']),'source_files_current':source['source_files'],'whole_definition_proofs':0,'owner_fidelity':'pending','semantic_closure':'not-established','goal_status':'active','next_ready_unit':'I03.1'},indent=2,sort_keys=True))
if __name__=='__main__':main()

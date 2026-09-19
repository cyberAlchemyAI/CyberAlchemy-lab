"""Advance exactly the tested 83 targets; preserve the original 195 denominator."""
import json
import subprocess
import sys
from collections import Counter
from support import ROOT, LAB, PREVIOUS, load, dump, sha, binding, need

def build():
    result=subprocess.run([sys.executable,'-c','import json,reconcile; print(json.dumps(reconcile.build()))'],cwd=PREVIOUS,capture_output=True,text=True,check=True)
    data=json.loads(result.stdout); entries=load(ROOT/'registry.json')['entries']; tests=load(ROOT/'receipts/target-validation.json')
    need(tests['result']=='PASS','Behavioral checks did not pass')
    need(len(entries)==83 and set(tests['targets'])=={x['target_id'] for x in entries},'Missing per-target validation')
    rows={x['target_id']:x for x in data['targets']}
    for entry in entries:
        target=entry['target_id']; need(tests['targets'][target]['result']=='PASS','Target did not pass')
        need(sha(LAB/entry['path'])==entry['sha256'],'Target registry drift')
        need(rows[target]['construction_state']=='scaffold-only','Target frontier changed')
        rows[target].update(construction_state='constructed-candidate',evidence=[{**binding(LAB/entry['path']),'registry':str((ROOT/'registry.json').relative_to(LAB))}],next_action='review exact bounded candidate and limitations before any adoption')
    data['inputs'].append(binding(ROOT/'registry.json')); data['state_counts']=dict(sorted(Counter(x['construction_state'] for x in data['targets']).items()))
    need(len(data['targets'])==195 and data['state_counts']=={'admitted-current':13,'constructed-candidate':182},'Unexpected reconciliation totals')
    return data
if __name__=='__main__': dump(ROOT/'reconciliation.json',build())

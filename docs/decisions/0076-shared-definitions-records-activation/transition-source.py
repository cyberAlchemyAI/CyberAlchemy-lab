"""Prepare a fresh data branch at the admitted epoch; preserve original signed history."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'implementation/lab-runtime/v2'))
from lab_runtime.store import Store
from lab_runtime.common import load,encoded
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encoded(v))
store=Store(ROOT/'.local/lab-runtime/shared/current-store',ROOT)
key=Path.home()/'.config/cyberalchemy-lab/shared-records/operator.pem'
if not (store.path/'config.json').exists():store.initialize(load(ROOT/'implementation/lab-runtime/v2/profile.json'),'shared-lab-current-0076','principal:lab-shared-operator',key.with_suffix('.pub').read_text().strip())
data=store.replay(require_current=True)
original=load(HERE/'proposal.json');cfg=data['config']
proposal={**original,'proposal_id':'shared-records-source-transition-0076','expected_head':data['head']['transaction_digest'],'source_snapshot_digest':data['baseline']['snapshot_digest'],'scope_ref':cfg['scope_ref']}
prior=[tx for tx in data['transactions'][1:] if tx.get('proposal',{}).get('proposal_id')==proposal['proposal_id']]
if not prior:
 review=store.review(proposal);put(HERE/'source-transition/proposal.json',proposal)
 put(HERE/'source-transition/approval.json',store.authorize(proposal,key))
 put(HERE/'source-transition/native-review.json',review)
else:assert prior[0]['proposal']==load(HERE/'source-transition/proposal.json')
print(json.dumps({'status':'prepared','source_cut':data['baseline']['snapshot_digest']}))

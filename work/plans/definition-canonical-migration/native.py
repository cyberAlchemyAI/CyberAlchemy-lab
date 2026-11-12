from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'implementation/lab-runtime/v2'))
from lab_runtime.store import Store
from lab_runtime.common import load,encoded
key=Path.home()/'.config/cyberalchemy-lab/shared-records/operator.pem'
store=Store(R/'.local/lab-runtime/shared/migration-0077-store',R)
if not (store.path/'config.json').exists():store.initialize(load(R/'implementation/lab-runtime/v2/profile.json'),'shared-lab-definitions-v2-0077','principal:lab-shared-operator',key.with_suffix('.pub').read_text().strip())
data=store.replay(require_current=True)
proposal=load(R/'docs/decisions/0076-shared-definitions-records-activation/proposal.json');cfg=data['config']
proposal.update(proposal_id='shared-lab-source-transition-0077',expected_head=data['head']['transaction_digest'],source_snapshot_digest=data['baseline']['snapshot_digest'],scope_ref=cfg['scope_ref'])
P.joinpath('transfer-proposal.json').write_bytes(encoded(proposal))
prior=[tx for tx in data['transactions'][1:] if tx['proposal']['proposal_id']==proposal['proposal_id']]
if not prior:
 P.joinpath('transfer-review.json').write_bytes(encoded(store.review(proposal)))
 P.joinpath('transfer-approval.json').write_bytes(encoded(store.authorize(proposal,key)))
P.joinpath('NATIVE-CONTEXT.json').write_text(json.dumps({'store':str(store.path.relative_to(R)),'cut':data['baseline']['snapshot_digest'],'head':data['head'],'config':cfg,'freshness':data['freshness']},indent=2)+'\n')
print(json.dumps({'status':'prepared','cut':data['baseline']['snapshot_digest'],'head':data['head']['sequence']}))

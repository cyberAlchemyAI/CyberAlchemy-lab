"""Prepare exact signed proposals in disposable regression stores only."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'implementation/lab-runtime/v2'))
from lab_runtime.store import Store
from lab_runtime.cli import example
from lab_runtime.common import load,encoded
request=json.load(sys.stdin)
home=Path(request['home']).resolve()
assert str(home).startswith('/tmp/')
store=Store(home/'store',ROOT);data=store.replay(require_current=True)
if request['kind']=='work':proposal=example(store,'r5-unrelated-publication')
else:
 old=request['target'];record=dict(old['record']);record['version']='1.0.0-candidate.2'
 target={**old,'operation':'revise','version_ref':record['definition_id']+'@'+record['version'],
 'predecessor_ref':old['version_ref'],'record':record,'decision_ref':'decision:fixture:r5-successor'}
 cfg=data['config']
 proposal={'schema_version':'lab-runtime-proposal/v1','proposal_id':'r5-successor',
 'expected_head':data['head']['transaction_digest'],'source_snapshot_digest':data['baseline']['snapshot_digest'],
 'scope_ref':cfg['scope_ref'],'policy_ref':cfg['policy_ref'],'challenge_route':cfg['challenge_route'],'targets':[target],'schemas':{}}
review=store.review(proposal);approval=store.authorize(proposal,home/'owner.pem')
prefix=request['prefix']
for name,value in [('proposal',proposal),('approval',approval),('review',review)]:
 (home/(prefix+'-'+name+'.json')).write_bytes(encoded(value))
print(json.dumps({'proposal':proposal,'approval':approval,'review':review}))

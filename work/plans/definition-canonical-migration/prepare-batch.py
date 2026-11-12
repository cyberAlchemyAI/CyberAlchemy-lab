from pathlib import Path
import json,sys,fcntl
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'implementation/lab-runtime/v2'))
sys.path.insert(0,str(R/"implementation/lab-runtime/alchlang/shared-records"))
from schema_metadata_cache import install
from jsonschema import Draft202012Validator
install(Draft202012Validator)
from lab_runtime.store import Store
from lab_runtime.common import load,encoded
index=int(sys.argv[1]);b=P/'batches'/('unit-%02d'%index);b.mkdir(parents=True,exist_ok=True)
lock=(b/'.prepare.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
ctx=load(P/'NATIVE-CONTEXT.json');store=Store(R/ctx['store'],R);data=store.replay(require_current=True)
selected=load(R/'docs/decisions/0077-definition-v2-canonical-migration/authorization.json')['accepted_definitions'][(index-1)*8:index*8]
mapping={x['definition_id']:x for x in load(R/'work/plans/definition-catalog-v2-layout/MAPPING.json')['entries']}
if not (b/'proposal.json').exists():
 targets=[]
 for x in selected:
  body=load(R/x['source']['path']);old=mapping[body['definition_id']]['source'];targets.append({'category':'definition','operation':'revise','version_ref':x['version'],'carrier_ref':'cal.artifact-type.definition/v2','record':body,'predecessor_ref':body['definition_id']+'@'+old['version'],'decision_ref':'decision:definition-v2-canonical-migration-0077:'+body['definition_id'],'contract':None})
 cfg=data['config'];proposal={'schema_version':'lab-runtime-proposal/v1','proposal_id':'definition-v2-canonical-0077-unit-%02d'%index,'expected_head':data['head']['transaction_digest'],'source_snapshot_digest':ctx['cut'],'scope_ref':cfg['scope_ref'],'policy_ref':cfg['policy_ref'],'challenge_route':cfg['challenge_route'],'targets':targets,'schemas':{}}
 (b/'proposal.json').write_bytes(encoded(proposal))
 (b/'context.json').write_bytes(encoded({'head':data['head'],'source_cut':ctx['cut'],'source_freshness':data['freshness'],'project':data['projection']['state']['payload']['project_ref']}))
proposal=load(b/'proposal.json');committed=[tx for tx in data['transactions'][1:]if tx['proposal']['proposal_id']==proposal['proposal_id']]
if not committed:
 if not (b/'native-review.json').exists():(b/'native-review.json').write_bytes(encoded(store.review(proposal)))
 if not (b/'approval.json').exists():(b/'approval.json').write_bytes(encoded(store.authorize(proposal,Path.home()/'.config/cyberalchemy-lab/shared-records/operator.pem')))
else:assert committed[0]['proposal']==proposal
print(json.dumps({'batch':index,'targets':len(proposal['targets']),'committed':bool(committed)}))

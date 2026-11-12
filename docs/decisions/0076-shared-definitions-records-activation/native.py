"""Provision and prepare the explicitly authorized activation; apply is shared-gated."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'implementation/lab-runtime/v2'))
from lab_runtime.store import Store,keygen
from lab_runtime.common import load,encoded
HERE=Path(__file__).resolve().parent
LOCAL=ROOT/'.local/lab-runtime/shared'
KEY=Path.home()/'.config/cyberalchemy-lab/shared-records/operator.pem'
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encoded(v))
def prepare():
 if (HERE/'decision.json').exists():
  raise RuntimeError('Admission 0076 is immutable; use the shared restore/activate and explicit carry-forward workflow, not native preparation.')
 auth=load(HERE/'authorization.json');assert auth['authorized'] is True
 KEY.parent.mkdir(parents=True,exist_ok=True,mode=0o700);KEY.parent.chmod(0o700)
 if not KEY.exists():keygen(KEY,KEY.with_suffix('.pub'))
 KEY.chmod(0o600)
 store=Store(LOCAL/'native-store',ROOT)
 if not (store.path/'config.json').exists():store.initialize(load(ROOT/'implementation/lab-runtime/v2/profile.json'),'shared-lab-0076','principal:lab-shared-operator',KEY.with_suffix('.pub').read_text().strip())
 data=store.replay(require_current=True)
 schema=load(ROOT/'implementation/lab-runtime/alchlang/shared-records/contracts/definition-registry-v2.schema.json')
 schema_path='runtime/schemas/definition-registry-v2-0076.json'
 desc={'artifact_type_ref':'cal.artifact-type.definition-registry/v2','semantic_kind':'definition-registry','semantic_definition_refs':['cal.definition.definition@1.0.0-candidate.1','cal.definition.artifact-type-registry@1.0.0-candidate.1'],'schema_path':schema_path,'schema_selector':None,'schema_sha256':hashlib.sha256(encoded(schema)).hexdigest(),'distinct_validation_purpose':'A mixed Definition/v1-v2 registry retaining exact original bodies, carrier/schema/generator/admission provenance, owner dispositions, current lookup and publication decision.'}
 contract={k:desc[k] for k in ['semantic_kind','schema_path','schema_sha256','schema_selector']}
 contract.update(instance_discriminator={'path':'/schema_version','value':'cyberalchemy-lab-definition-registry/v2'},identity_field='schema_version',allowed_relation_kinds=[],relation_roles=[])
 put(HERE/'registry-descriptor.json',desc)
 put(HERE/'registry-native-contract.json',contract)
 targets=[]
 for t in auth['accepted_definitions']:
  raw=(ROOT/t['source']['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==t['source']['sha256']
  body=json.loads(raw)
  targets.append({'category':'definition','operation':'admit','version_ref':t['version'],'carrier_ref':'cal.artifact-type.definition/v2','record':body,'predecessor_ref':None,'decision_ref':'decision:shared-definitions-records-0076:'+body['definition_id'],'contract':None})
 targets.append({'category':'artifact-type','operation':'admit','version_ref':desc['artifact_type_ref'],'carrier_ref':'cal.artifact-type.artifact-type/v3','record':desc,'predecessor_ref':None,'decision_ref':'decision:shared-definitions-records-0076:registry-v2','contract':contract})
 cfg=data['config']
 proposal={'schema_version':'lab-runtime-proposal/v1','proposal_id':'shared-definitions-records-activation-0076','expected_head':data['head']['transaction_digest'],'source_snapshot_digest':data['baseline']['snapshot_digest'],'scope_ref':cfg['scope_ref'],'policy_ref':cfg['policy_ref'],'challenge_route':cfg['challenge_route'],'targets':targets,'schemas':{schema_path:schema}}
 # Frozen proposal is retained after a commit; never prepare against a later HEAD.
 if (HERE/'proposal.json').exists():
  proposal=load(HERE/'proposal.json')
 committed=[tx for tx in data['transactions'][1:] if tx.get('proposal',{}).get('proposal_id')==proposal['proposal_id']]
 if committed:
  assert len(committed)==1 and committed[0]['proposal']==proposal
  print(json.dumps({'status':'already-committed','transaction':committed[0]['digest']}));return
 review=store.review(proposal)
 if not (HERE/'proposal.json').exists():
  put(HERE/'proposal.json',proposal);put(HERE/'approval.json',store.authorize(proposal,KEY))
 put(HERE/'receipts/native-review.json',review)
 print(json.dumps({'status':'prepared','source_cut':proposal['source_snapshot_digest'],'project':data['projection']['state']['payload']['project_ref'],'targets':len(proposal['targets'])}))
if __name__=='__main__':prepare()

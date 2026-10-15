"""Read-only independent retained public proof verification; no constructor or replay."""
import base64,hashlib,json
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent;PREP=HERE.parents[1];family=PREP/'instances/optimized-0002';folder=family/'context/packages/0001'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
proof=json.loads((folder/'authentication-proof.json').read_bytes());policy=json.loads((folder/'host-permission-public.json').read_bytes());trusted=json.loads((folder/'trusted-context.json').read_bytes());request=json.loads((folder/'request.json').read_bytes());phase=json.loads((PREP/'reports/optimized-0002-context.json').read_bytes())
wire=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'],validate=True)).verify(base64.b64decode(proof['signature'],validate=True),wire(proof['challenge']))
assert proof['challenge']['policy_sha256']==bind(folder/'host-permission-public.json')['sha256']
assert trusted['authentication_evidence_binding']['sha256']==bind(folder/'authentication-proof.json')['sha256']
assert trusted['connection_ref']==proof['challenge']['connection_ref'] and trusted['host_instance_ref']==proof['challenge']['host_instance_ref']
assert request['actor']['principal_ref']==trusted['principal_ref']==policy['principal_ref']
assert policy['scope_ref'] in trusted['scope_refs']
assert policy['period_binding']==bind(family/'source/packages/0001/period.json')
assert datetime.fromisoformat(policy['not_before'])<=datetime.fromisoformat(phase['ended_at'])<datetime.fromisoformat(policy['expires_at'])
assert int((datetime.fromisoformat(policy['expires_at'])-datetime.fromisoformat(policy['not_before'])).total_seconds())<=1201
assert policy['max_session_seconds']==900 and policy['allowed_operations']==['context.get','session.open']
old_folder=RUN_OLD=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/optimized-family-preparation-0001/instances/optimized-0001/context/packages/0001'
old_policy=json.loads((old_folder/'host-permission-public.json').read_bytes());old_proof=json.loads((old_folder/'authentication-proof.json').read_bytes())
assert old_policy['reader_public_key']!=policy['reader_public_key'] and old_proof['challenge']['nonce']!=proof['challenge']['nonce'] and old_proof['challenge']['connection_ref']!=proof['challenge']['connection_ref']
result={'fresh_key_nonce_connection_distinct_from_failed_v1':True,'schema_version':'lab-T02-retained-Context-public-authentication-proof/v1-candidate','result':'PASS-public-proof-only','bindings':[bind(folder/name) for name in ['authentication-proof.json','host-permission-public.json','trusted-context.json','request.json']],'real_independent_Ed25519_challenge_signature_verified':True,'challenge_policy_and_trusted_proof_links_verified':True,'actual_actor_principal_scope_matches_fresh_grant':True,'grant_unexpired_at_original_failed_phase_terminal':True,'fixed_grant_period_and_900second_session_budget_verified':True,'new_grant_created_or_renewed':False,'original_callbacks_or_constructor_executed':False,'Context_delivery_materialization_passed':True,'authority_effect':'none','actual_owner_outcome':None}
with (HERE/'authentication-verification.json').open('x') as output:json.dump(result,output,sort_keys=True,indent=2);output.write('\n')
print(json.dumps({'result':result['result'],'verification_binding':bind(HERE/'authentication-verification.json')},sort_keys=True))

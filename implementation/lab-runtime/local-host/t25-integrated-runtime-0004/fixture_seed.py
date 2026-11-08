"""Explicit synthetic fixture archive audit; never accepts arbitrary live inputs."""
import base64
import hashlib
import json
from pathlib import Path
SEED=Path('/home/vlad_/.local/share/cyberalchemy-lab/t15-integrated-private-0001/legacy-local-4636eca980a5d94d/branch.snapshot')
PIN='3384b150e863f96e1b67b4d7a5d644f5545703afc567515de18c7630751c8af5'
TARGET='.cal-fixture-seed/branch.snapshot'
def audit(seed=SEED,pin=PIN):
 raw=Path(seed).read_bytes();need=lambda x,m:None if x else (_ for _ in ()).throw(ValueError(m))
 need(hashlib.sha256(raw).hexdigest()==pin,'exact selected synthetic fixture seed differs');v=json.loads(raw)
 need(v['schema_version']=='lab-owned-custody-participation-archive/v1-candidate' and v['private_keys_exported'] is False and v['Session_memory_rehydrated'] is False and v['authority_effect']=='none' and v['actual_owner_outcome'] is None,'fixture seed claim ceiling differs')
 expected={'HEAD.json','baseline.json','config.json','transactions/0000000000.json','transactions/0000000001.json','transactions/0000000002.json'}
 need(set(v['files'])==expected,'fixture seed file set differs')
 def inspect(value):
  if isinstance(value,dict):
   for k,w in value.items():
    need(k.lower() not in ('private_key','private_key_pem','secret_key','password','access_token','refresh_token','client_secret','reader_private_policy','issuer_private_policy'),'private credential/policy field in fixture seed')
    inspect(w)
  elif isinstance(value,list):
   for w in value:inspect(w)
  elif isinstance(value,str):need('-----BEGIN PRIVATE KEY-----' not in value and '-----BEGIN OPENSSH PRIVATE KEY-----' not in value,'private signing key in fixture seed')
 for name,row in v['files'].items():
  need(set(row)=={'base64_original_bytes','sha256'},'fixture seed file descriptor differs')
  payload=base64.b64decode(row['base64_original_bytes'],validate=True)
  need(hashlib.sha256(payload).hexdigest()==row['sha256'],'fixture seed original bytes differ');inspect(json.loads(payload))
 return raw,{'result':'PASS-explicit-synthetic-seed-audit','seed_sha256':pin,'archive_members_checked':sorted(expected),'private_keys_exported':False,'Session_memory_rehydrated':False,'credential_and_private_policy_fields_found':False,'fixture_only':True,'original_protected_Source8':False,'authority_effect':'none','actual_owner_outcome':None}
if __name__=='__main__':print(json.dumps(audit()[1],sort_keys=True))

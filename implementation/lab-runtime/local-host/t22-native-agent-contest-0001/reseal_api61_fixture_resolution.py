"""Reseal only the unexecuted additive fixture API61 cut."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
NEW=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v61-t22-fixture-resolution-0001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
prefix=NEW.relative_to(ROOT).as_posix()+'/'
profile=json.loads((NEW/'contract-profile.json').read_bytes())
for r in profile['files']:
 if r['path'].startswith(prefix):r['sha256']=sha(ROOT/r['path'])
profile['integration_members_binding']['sha256']=sha(NEW/'integration-members.json');save(NEW/'contract-profile.json',profile)
source=json.loads((NEW/'source-manifest.json').read_bytes())
for r in source['files']:
 if r['path'].startswith(prefix):r['sha256']=sha(ROOT/r['path'])
source['profile_binding']['sha256']=sha(NEW/'contract-profile.json');save(NEW/'source-manifest.json',source)
receipt=json.loads((NEW/'rebind-receipt.json').read_bytes());receipt.update(successor_manifest_sha256=sha(NEW/'source-manifest.json'),successor_profile_sha256=sha(NEW/'contract-profile.json'));save(NEW/'rebind-receipt.json',receipt)
print(json.dumps(receipt,sort_keys=True))

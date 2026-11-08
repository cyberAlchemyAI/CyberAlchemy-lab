"""Seal the candidate-lineage-hardened fixture resolver from API63."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v62-t22-fixture-resolution-0001';NEW=BASE/'api-integration-v63-t22-fixture-resolution-0001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def main():
 if sha(OLD/'source-manifest.json')!='e9e8af7f6090a80446c4c01a9d08b725f4a31ce40a90ccbb53cf740e4598afa6' or NEW.exists():raise ValueError('exact predecessor/disjoint output required')
 source=json.loads((OLD/'source-manifest.json').read_bytes());profile=json.loads((OLD/'contract-profile.json').read_bytes())
 prefix=rel(OLD)+'/'
 NEW.mkdir(mode=0o700)
 for row in source['files']:
  if row['path'].startswith(prefix):
   target=NEW/row['path'][len(prefix):];target.parent.mkdir(parents=True,exist_ok=True)
   if sha(ROOT/row['path'])!=row['sha256']:raise ValueError('predecessor changed')
   shutil.copy2(ROOT/row['path'],target)
 for name in ['fixture_resolution_source.py','fixture_resolution_handler.py']:
  raw=(HERE/name.replace('.py','_v2.py')).read_text().replace('ROOT = Path(__file__).resolve().parents[4]','from .source_bridge import ROOT')
  compile(raw,str(NEW/name),'exec');(NEW/name).write_text(raw)
 def rebind(row):
  if row['path'].startswith(prefix):
   p=NEW/row['path'][len(prefix):];return {'path':rel(p),'sha256':sha(p)}
  return row
 profile['files']=sorted([rebind(r) for r in profile['files']],key=lambda r:r['path'])
 profile['integration_members_binding']={'path':rel(NEW/'integration-members.json'),'sha256':sha(NEW/'integration-members.json')}
 save(NEW/'contract-profile.json',profile)
 source['files']=sorted([rebind(r) for r in source['files']],key=lambda r:r['path']);source['profile_binding']={'path':rel(NEW/'contract-profile.json'),'sha256':sha(NEW/'contract-profile.json')}
 for r in source['files']:
  if r['path']==source['profile_binding']['path']:r['sha256']=source['profile_binding']['sha256']
 source['predecessor_source_manifest_binding']={'path':rel(OLD/'source-manifest.json'),'sha256':sha(OLD/'source-manifest.json')};save(NEW/'source-manifest.json',source)
 receipt={'schema_version':'lab-T22-fixture-resolution-hardened-rebind/v1','successor_package':rel(NEW),
  'successor_manifest_sha256':sha(NEW/'source-manifest.json'),'successor_profile_sha256':sha(NEW/'contract-profile.json'),'authority_effect':'none'}
 save(NEW/'rebind-receipt.json',receipt);print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()

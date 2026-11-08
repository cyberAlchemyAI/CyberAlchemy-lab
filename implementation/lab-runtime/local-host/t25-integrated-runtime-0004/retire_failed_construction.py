"""Retain failed provisional controls before advancing an owned install stage."""
import argparse,hashlib,json,os
from pathlib import Path

def need(value,reason):
 if not value:raise ValueError(reason)
def retire(root,receipt_pin,attempt):
 root=Path(root).resolve();private=root.parent/'.cal-runtime';receipt=private/'installation.json';raw=receipt.read_bytes();value=json.loads(raw)
 need(hashlib.sha256(raw).hexdigest()==receipt_pin and value['phase']=='construct-context','only exact provisional selection can be retired')
 need(attempt.isalnum(),'closed failed-attempt identity required')
 # Do not invalidate a native construction that is still using these inputs.
 for process in Path('/proc').iterdir():
  if not process.name.isdigit() or int(process.name)==os.getpid():continue
  try:args=(process/'cmdline').read_bytes().split(b'\0')
  except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  need(not any(arg.startswith(os.fsencode(str(prefix)+'/')) for arg in args for prefix in (root,private)), 'selected construction process is still alive: '+process.name)
 names=('launcher.json','installation.json','bindings/host-selection.json','construction-selection.json')
 for name in names:
  source=private/name
  need(source.is_file() and not source.is_symlink() and source.stat().st_uid==os.getuid() and source.stat().st_mode&0o777==0o600,'failed provisional control custody differs')
 destination=private/'failed-attempts'/attempt;destination.mkdir(mode=0o700,parents=True,exist_ok=False)
 package=json.loads((root/'.cal-package-manifest.json').read_bytes())
 # Retain the actual generated cold observation before the next constructor
 # resets provisional metadata from its public templates.
 cold=root/package['binding_paths']['family.cold']
 if cold.exists():
  need(cold.is_file() and not cold.is_symlink(),'failed cold observation custody differs')
  retained=destination/'actual-source-cold.json';retained.write_bytes(cold.read_bytes());retained.chmod(0o600)
 for name in names:
  source=private/name
  target=destination/name;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);os.rename(source,target)
 return {'result':'PASS-failed-provisional-controls-retained','retired_receipt_sha256':receipt_pin,'retained_at':str(destination),'ready_runtime_changed':False,'authority_effect':'none'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('receipt_sha256');p.add_argument('attempt');a=p.parse_args();print(json.dumps(retire(a.root,a.receipt_sha256,a.attempt),sort_keys=True))

#!/usr/bin/env python3
"""Check the current combined retention selection without changing Git."""
from pathlib import Path
import gzip,json,os,subprocess,hashlib,argparse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  while block:=stream.read(1024*1024):h.update(block)
 return h.hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--verify-local-archive',action='store_true')
 parser.add_argument('--verify-required-inputs',action='store_true')
 args=parser.parse_args()
 if args.verify_required_inputs and (HERE/'ACTUAL-DEPENDENCIES.json.gz').exists():
  command=[__import__('sys').executable,str(HERE/'check_actual_dependencies.py')]
  if args.verify_local_archive:command.append('--verify-local-archive')
  return subprocess.call(command,cwd=ROOT)
 result=json.loads((HERE/'RESULT.json').read_text())
 with gzip.open(HERE/'selection.json.gz','rt') as stream:selection=json.load(stream)
 removed={row['path'] for row in selection['files']}
 current={os.fsdecode(x) for x in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(bytes([0])) if x}
 errors=[]
 if len(removed)!=len(selection['files']):errors.append('Duplicate retired paths')
 if removed & current:errors.append('Retired paths tracked again')
 if any(os.path.lexists(ROOT/path) for path in removed):errors.append('Retired paths recreated')
 checks=json.loads((HERE/'CHECKS.json').read_text())
 latest={row['name']:row for row in checks if row['phase']=='after'}
 if len(latest)!=10 or any(row['exit_code']!=0 for row in latest.values()):errors.append('Current checks incomplete or failed')
 for name in ['runtime-v1','runtime-v2']:
  before=next(row for row in checks if row['phase']=='before' and row['name']==name)
  if before['stdout']!=latest[name]['stdout']:errors.append('Runtime baseline changed: '+name)
 for group in result['retired_release_groups_ignored']:
  if subprocess.run(['git','check-ignore','--no-index','--',group+'/retired-source.py'],cwd=ROOT,capture_output=True).returncode:errors.append('Retired source ignore missing: '+group)
 if args.verify_local_archive:
  for archive in result['archives']:
   path=ROOT/archive['path']
   if not path.is_file() or sha(path)!=archive['sha256']:errors.append('Local archive unavailable or changed: '+archive['path'])
 if args.verify_required_inputs:
  local=ROOT/'.local/history-cleanup-20261108-apply'
  with gzip.open(local/'protected-input-hashes.json.gz','rt') as stream:inputs=json.load(stream)
  policy=result['intentional_policy_changes']
  for row in inputs:
   path=ROOT/row['path'];expected=policy[row['path']]['after_sha256'] if row['path'] in policy else row['sha256']
   if not path.is_file() or sha(path)!=expected:errors.append('Required input changed: '+row['path'])
 report=dict(status='fail' if errors else 'pass',tracked_now=len(current),retired_paths=len(removed),current_checks=len(latest),local_archives_verified=args.verify_local_archive,required_inputs_verified=args.verify_required_inputs,errors=errors)
 print(json.dumps(report,indent=2))
 return bool(errors)
if __name__=='__main__':raise SystemExit(main())

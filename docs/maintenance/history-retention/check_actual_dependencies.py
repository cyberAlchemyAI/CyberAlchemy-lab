#!/usr/bin/env python3
"""Verify current executable inputs and the applied retirement, without changing Git."""
import argparse,gzip,hashlib,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while block:=f.read(1048576):h.update(block)
 return h.hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--verify-local-archive',action='store_true')
 args=parser.parse_args()
 with gzip.open(HERE/'ACTUAL-DEPENDENCIES.json.gz','rt') as f:data=json.load(f)
 current={os.fsdecode(p) for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(b'\0') if p}
 errors=[]
 for row in data['retired_files']:
  p=ROOT/row['path']
  if row['path'] in current or os.path.lexists(p):errors.append('Retired path present: '+row['path'])
 for row in data['observed_inputs']:
  p=ROOT/row['path']
  if not p.is_file() or digest(p)!=row['sha256']:errors.append('Observed input missing or changed: '+row['path'])
 for row in data['checks']:
  if row['exit_code']!=0:errors.append('Check failed: '+row['name'])
 if args.verify_local_archive:
  p=ROOT/data['archive']['path']
  if not p.is_file() or digest(p)!=data['archive']['sha256']:errors.append('Archive missing or changed')
 report={'status':'fail' if errors else 'pass','tracked_now':len(current),'retired_this_pass':len(data['retired_files']),'observed_inputs_verified':len(data['observed_inputs']),'successful_checks':len(data['checks']),'errors':errors}
 print(json.dumps(report,indent=2))
 return bool(errors)
if __name__=='__main__':raise SystemExit(main())

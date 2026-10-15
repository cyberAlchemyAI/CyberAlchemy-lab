"""Preserve partial evidence and request SIGINT only for exact owned test PIDs."""
import hashlib,json,os,signal
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
CHOICE=RUN/'API45-sequential-verification-choice-0001.json'
PREFIX='product/lab/release-candidates/v1/interface/'
PYTHON='/tmp/cal-R02-environment-0001/bin/python'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def main():
 choice=json.loads(CHOICE.read_bytes())
 successor=ROOT/PREFIX/'api-v45/source-manifest.json'
 assert successor.is_file(),'successor must be frozen first'
 source=json.loads(successor.read_bytes())
 assert source['authority_effect']=='none' and source['actual_owner_outcome'] is None
 snapshots=RUN/'superseded-test-interrupt-snapshots-0001';snapshots.mkdir(mode=0o700)
 rows=[]
 for expected in choice['expected_owned_jobs']:
  matches=[]
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:
    args=[a.decode() for a in p.joinpath('cmdline').read_bytes().split(b'\0') if a]
    if len(args)<5 or args[:3]!=[PYTHON,'-B',PREFIX+expected['test_script']]:continue
    assert p.stat().st_uid==os.getuid()
    assert args[args.index('--source-sha256')+1]==expected['source_sha256']
    log=Path(os.readlink(p/'fd/1'))
    assert log.is_absolute() and log.is_relative_to(RUN) and log.suffix=='.log' and not log.is_symlink()
    assert log.stat().st_size<=64*1024*1024
    stat=p.joinpath('stat').read_text();start=stat[stat.rindex(')')+2:].split()[19]
    matches.append((int(p.name),args,log,start))
   except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  assert len(matches)<=1,'ambiguous exact owned job'
  for pid,args,log,start in matches:
   snapshot=snapshots/(str(expected['session_id'])+'.log')
   raw=log.read_bytes()
   fd=os.open(snapshot,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
   with os.fdopen(fd,'wb') as f:f.write(raw)
   row={**expected,'pid':pid,'proc_start_ticks':start,'argv':args,
        'stdout_path':log.relative_to(ROOT).as_posix(),'pre_interrupt_snapshot':bind(snapshot),
        'requested_signal':'SIGINT','terminal_state':'not-yet-observed','complete_full_suite':False,
        'cleanup_established':False,'authority_effect':'none'}
   # Revalidate identity immediately before addressing the PID.
   p=Path('/proc')/str(pid)
   actual=[a.decode() for a in p.joinpath('cmdline').read_bytes().split(b'\0') if a]
   stat=p.joinpath('stat').read_text()
   assert actual==args and stat[stat.rindex(')')+2:].split()[19]==start
   os.kill(pid,signal.SIGINT);rows.append(row)
 report={'schema_version':'lab-owned-test-interrupt-request/v1-candidate','choice_binding':bind(CHOICE),
         'successor_source_binding':bind(successor),'jobs':rows,'actual_owner_outcome':None,'authority_effect':'none',
         'claim_ceiling':'Controlled SIGINT requests only. Actual terminals, cleanup and full successor verification must be observed independently; no full suite verdict inferred.'}
 with (RUN/'owned-test-interrupt-requests-0001.json').open('x') as f:
  json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'requested_SIGINT_count':len(rows),'actual_pids':[x['pid'] for x in rows]}),flush=True)
if __name__=='__main__':main()

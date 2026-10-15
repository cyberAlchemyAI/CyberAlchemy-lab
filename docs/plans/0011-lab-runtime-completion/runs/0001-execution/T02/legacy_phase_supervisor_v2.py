"""Bounded one-shot owned source construction; no listener or automatic restart."""
import argparse
from datetime import datetime,timezone
import hashlib
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
FAMILY=ROOT/'product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001'
INSTALLATION=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v1-completion-0001/installations/0001'
PYTHON=INSTALLATION/'bin/python'
def stamp():return datetime.now(timezone.utc).isoformat()
def write(path,value):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def identity(pid):
    # Only owned process identity; no frame locals, memory or credential contents.
    stat=Path('/proc')/str(pid)/'stat';fields=stat.read_text().rsplit(') ',1)[1].split()
    return {'pid':pid,'start_ticks':int(fields[19]),'uid':os.getuid()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--instance',required=True);p.add_argument('--phase',required=True,choices=['source','cold','reader','mapped','context']);p.add_argument('--max-seconds',type=int,default=3600);a=p.parse_args()
    target=FAMILY/'instances'/a.instance
    if not target.is_dir() or target.parent!=FAMILY/'instances' or not 1<=a.max_seconds<=3600:raise ValueError('bounded exact owned instance required')
    command=[str(PYTHON),'-I','-B','-c',"import sys,runpy;sys.path.insert(0,sys.argv[1]);sys.argv=sys.argv[2:];runpy.run_path(sys.argv[0],run_name='__main__')",str(INSTALLATION/'deps'),str(FAMILY/'construct_legacy_v2.py'),'--instance',a.instance,'--phase',a.phase]
    lease=None
    if a.phase=='context':
        lease=open(HERE.parent/'lease-sensitive-runtime.lock','a+');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
    started=stamp();log=HERE/(a.instance+'-'+a.phase+'-attempt0002.log');fd=os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as output:
        env=dict(os.environ,PYTHONPATH=str(INSTALLATION/'deps'),PYTHONDONTWRITEBYTECODE='1');child=subprocess.Popen(command,cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        write(HERE/(a.instance+'-'+a.phase+'-attempt0002-supervisor-start.json'),{'schema_version':'lab-T02-source-supervisor-start/v1-candidate','started_at':started,'supervisor':identity(os.getpid()),'child':identity(child.pid),'command':command,'max_seconds':a.max_seconds,'driver_sha256':hashlib.sha256((FAMILY/'construct_legacy_v2.py').read_bytes()).hexdigest(),'authority_effect':'none','automatic_restart':False})
        timed_out=False
        try:exit_code=child.wait(timeout=a.max_seconds)
        except subprocess.TimeoutExpired:
            timed_out=True;os.killpg(child.pid,signal.SIGTERM)
            try:exit_code=child.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);exit_code=child.wait()
    report=HERE/(a.instance+'-'+a.phase+'-attempt0002.json')
    write(HERE/(a.instance+'-'+a.phase+'-attempt0002-supervisor-terminal.json'),{'schema_version':'lab-T02-source-supervisor-terminal/v1-candidate','started_at':started,'ended_at':stamp(),'instance':a.instance,'phase':a.phase,'actual_exit_code':exit_code,'timed_out':timed_out,'phase_report_exists':report.exists(),'phase_report_sha256':hashlib.sha256(report.read_bytes()).hexdigest() if report.exists() else None,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'authority_effect':'none','automatic_restart':False,'cleanup_claimed_by_supervisor':False})
    if lease is not None:fcntl.flock(lease,fcntl.LOCK_UN);lease.close()
    raise SystemExit(0 if exit_code==0 else 1)
if __name__=='__main__':main()

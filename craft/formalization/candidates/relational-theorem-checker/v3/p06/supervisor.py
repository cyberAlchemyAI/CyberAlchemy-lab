"""Owned process groups, bounded output, deadlines and explicit memory modes.

Advisory RSS sampling is a best-effort early stop, never a hard RSS guarantee.
Cgroup enforcement is conditional on a writable delegated v2 parent.
"""
from pathlib import Path
from dataclasses import dataclass
import fcntl
import copy
import json
import os
import selectors
import signal
import subprocess
import tempfile
import time
import uuid
from ..p03.context import BASE,C,require,binding

HERE=Path(__file__).resolve().parent

def membership():
    rows=Path('/proc/self/cgroup').read_text().splitlines()
    return next((r.split(':',2)[2] for r in rows if r.startswith('0::')),None)

def capabilities(parent=None):
    mount=Path('/sys/fs/cgroup');current=membership()
    root=Path(parent).resolve() if parent is not None else (mount/(current or '/').lstrip('/')).resolve()
    valid=root.is_relative_to(mount) and root.is_dir()
    available=(root/'cgroup.controllers').read_text().split() if valid and (root/'cgroup.controllers').exists() else []
    enabled=(root/'cgroup.subtree_control').read_text().split() if valid and (root/'cgroup.subtree_control').exists() else []
    writable=valid and os.access(root,os.W_OK)
    supported=bool(current and writable and {'memory','pids'}<=set(enabled))
    return {'schema':'relational.host-resource-capabilities/v3','cgroup_v2':current is not None,'current_membership':current,'delegated_parent':str(root),'controllers_available':available,'controllers_enabled':enabled,'parent_writable':writable,'required_memory_available':supported,'reason':'Writable delegated memory/pids controls available.' if supported else 'No writable delegated parent with enabled memory/pids controls.','memory_semantics':'cgroup v2 charged memory, including descendants; shared-page charge attribution differs from aggregate RSS. Advisory sampling gives no hard cap.','authority_effect':'none'}

class Cgroup:
    def __init__(self,parent,policy,pids_max):
        info=capabilities(parent);require(info['required_memory_available'],info['reason'])
        require(type(pids_max) is int and pids_max>=2,'explicit pids limit required')
        self.path=Path(info['delegated_parent'])/('relational-v3-'+uuid.uuid4().hex)
        self.path.mkdir();self.before={}
        try:
            for name,value in [('memory.max',policy['memory_bytes']),('pids.max',pids_max)]:
                p=self.path/name;p.write_text(str(value));require(p.read_text().strip()==str(value),'effective cgroup control mismatch')
            swap=self.path/'memory.swap.max'
            if swap.exists():swap.write_text('0');require(swap.read_text().strip()=='0','swap control mismatch')
            self.before=self.events()
        except BaseException:
            self.path.rmdir();raise
    def events(self):return {k:int(v) for k,v in (line.split() for line in (self.path/'memory.events').read_text().splitlines())}
    def attach(self,pid):
        (self.path/'cgroup.procs').write_text(str(pid))
        actual=Path('/proc/'+str(pid)+'/cgroup').read_text()
        require('0::/'+str(self.path.relative_to('/sys/fs/cgroup')) in actual,'worker cgroup attachment mismatch')
    def oom(self):return self.events().get('oom_kill',0)>self.before.get('oom_kill',0)
    def close(self):
        procs=self.path/'cgroup.procs'
        if procs.read_text().strip():
            kill=self.path/'cgroup.kill'
            if kill.exists():kill.write_text('1')
            else:
                for p in procs.read_text().splitlines():
                    try:os.kill(int(p),signal.SIGKILL)
                    except ProcessLookupError:pass
        for _ in range(50):
            if not procs.read_text().strip():self.path.rmdir();return
            time.sleep(.02)
        raise RuntimeError('owned cgroup not empty after teardown')

def group_processes(pgid):
    records=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            raw=(p/'stat').read_text();fields=raw[raw.rfind(')')+2:].split()
            if int(fields[2])==pgid:
                rss=int(fields[21])*os.sysconf('SC_PAGE_SIZE')
                records.append({'pid':int(p.name),'rss':rss,'state':fields[0]})
        except (FileNotFoundError,ProcessLookupError,PermissionError,ValueError):continue
    return records

def subreaper():
    # Reap adopted grandchildren after cancellation instead of leaving zombies.
    import ctypes
    libc=ctypes.CDLL(None,use_errno=True)
    previous=ctypes.c_int()
    require(libc.prctl(37,ctypes.byref(previous),0,0,0)==0,'subreaper state unavailable')
    require(libc.prctl(36,1,0,0,0)==0,'subreaper capability unavailable')
    return previous.value

def restore_subreaper(previous):
    import ctypes
    require(ctypes.CDLL(None,use_errno=True).prctl(36,previous,0,0,0)==0,'subreaper state restoration failed')

def teardown(process,pgid,cgroup=None):
    observed=[r['pid'] for r in group_processes(pgid)]
    try:os.killpg(pgid,signal.SIGTERM)
    except ProcessLookupError:pass
    until=time.monotonic()+.3
    while time.monotonic()<until and any(r['state']!='Z' for r in group_processes(pgid)):time.sleep(.02)
    try:os.killpg(pgid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait(timeout=5)
    # waitpid is restricted to the owned process group. Other jobs are untouched.
    until=time.monotonic()+3
    while time.monotonic()<until:
        try:
            child,_=os.waitpid(-pgid,os.WNOHANG)
        except ChildProcessError:child=0
        alive=group_processes(pgid)
        if not alive:return {'observed_pids':observed,'remaining_pids':[]}
        if not child:time.sleep(.02)
    raise RuntimeError('owned process group not fully reaped')

@dataclass
class Supervisor:
    run_root: Path
    policy: dict
    cgroup_parent: object=None
    pids_max: object=None

    def __post_init__(self):
        self.run_root=Path(self.run_root).resolve();require(self.run_root.is_relative_to(BASE),'supervised run root outside v3')
        self.policy=copy.deepcopy(self.policy)
        json.dumps(self.policy,allow_nan=False)
        C.validate('resource-policy',self.policy)
        self.live_events={}

    def run(self,command,cancel=None,*,raw_input=None,worker_sources=(),started=None):
        """Run a trusted command via the bootstrap gate; request data is not code."""
        started=time.monotonic() if started is None else started;info=capabilities(self.cgroup_parent)
        mode='cgroup-v2' if self.policy['memory_mode']=='required' and info['required_memory_available'] else 'advisory'
        base={'schema':'relational.supervised-run/v3','status':'refused','enforcement':mode,'outcome':'worker-failed','events':[],'policy_identity':C.identity(self.policy),'complete':False,'qualified_receipt':False,'application_authorized':False,'authority_effect':'none'}
        if cancel is not None and cancel.is_set():
            return {**base,'outcome':'cancelled','reason':'Cancelled before worker launch.','seconds':time.monotonic()-started}
        if self.policy['memory_mode']=='required' and not info['required_memory_available']:
            return {**base,'enforcement':'unavailable','outcome':'policy-unavailable','reason':info['reason'],'seconds':time.monotonic()-started}
        if mode=='cgroup-v2' and not (type(self.pids_max) is int and self.pids_max>=2):
            return {**base,'outcome':'policy-unavailable','reason':'Required backend needs an explicit operator process limit of at least two.','seconds':time.monotonic()-started}
        self.run_root.mkdir(parents=True,exist_ok=True);os.chmod(self.run_root,0o700)
        lock=HERE/'supervisor.lock';lock.parent.mkdir(parents=True,exist_ok=True)
        with lock.open('a+b') as owned_lock:
            try:fcntl.flock(owned_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:return {**base,'reason':'One supervised expensive worker is already active.','seconds':time.monotonic()-started}
            job=Path(tempfile.mkdtemp(prefix='job-',dir=self.run_root));os.chmod(job,0o700)
            group=None;process=None;previous_subreaper=None;streams=selectors.DefaultSelector();captured=bytearray();total=0;peak=0;observed=[];outcome='completed';reason='Worker completed under '+('advisory observation; no hard aggregate memory cap.' if mode=='advisory' else 'verified cgroup controls.')
            try:
                previous_subreaper=subreaper()
                if mode=='cgroup-v2':group=Cgroup(self.cgroup_parent,self.policy,self.pids_max)
                if raw_input is not None:
                    require(isinstance(raw_input,bytes) and len(raw_input)<=self.policy['work_limits']['input_bytes'],'raw input byte ceiling')
                    with (job/'request.raw').open('xb') as f:f.write(raw_input)
                    os.chmod(job/'request.raw',0o600)
                descriptor={'enforcement':mode,'policy':self.policy,'cgroup':str(group.path) if group else None,'pids_max':self.pids_max,'job':str(job),'worker_sources':list(worker_sources)}
                (job/'supervision.json').write_text(json.dumps(descriptor))
                bootstrap=HERE/'bootstrap.py'
                process=subprocess.Popen([str(Path(os.sys.executable)),str(bootstrap),str(job),*map(str,command)],start_new_session=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                pgid=process.pid
                if group:group.attach(process.pid)
                (job/'go').write_text('supervisor-released')
                for pipe in [process.stdout,process.stderr]:os.set_blocking(pipe.fileno(),False);streams.register(pipe,selectors.EVENT_READ)
                while True:
                    records=group_processes(pgid);rss=sum(r['rss'] for r in records);peak=max(peak,rss);observed.extend(r['pid'] for r in records)
                    if cancel is not None and cancel.is_set():outcome='cancelled';reason='Explicit cancellation.';break
                    if time.monotonic()-started>self.policy['run_seconds']:outcome='timeout';reason='Whole-run monotonic deadline.';break
                    if group and group.oom():outcome='oom';reason='Observed cgroup memory.events oom_kill increment.';break
                    if mode=='advisory' and rss>self.policy['memory_bytes']:outcome='oom';reason='Observed advisory aggregate RSS threshold; no kernel OOM or hard RSS guarantee.';break
                    for key,_ in streams.select(.02):
                        data=os.read(key.fileobj.fileno(),65536)
                        if not data:streams.unregister(key.fileobj);continue
                        total+=len(data);captured.extend(data[:max(0,self.policy['output_bytes']-len(captured))])
                        if total>self.policy['output_bytes']:outcome='output-limit';reason='Observed stdout/stderr byte ceiling.';break
                    if outcome!='completed':break
                    if process.poll() is not None and not streams.get_map():
                        if process.returncode!=0:outcome='worker-failed';reason='Worker exit code '+str(process.returncode)
                        elif any(r['state']!='Z' for r in group_processes(pgid)):outcome='worker-failed';reason='Worker exited with live descendants.'
                        break
                cleanup=teardown(process,pgid,group)
                if group and group.oom():outcome='oom';reason='Observed cgroup OOM during completion/cleanup.'
                base.update(status='completed' if outcome=='completed' else 'nonqualified',outcome=outcome,reason=reason,complete=outcome=='completed',seconds=time.monotonic()-started,job=str(job),output_bytes_observed=total,aggregate_rss_peak_observed=peak,observed_pids=sorted(set(observed)),cleanup=cleanup,events=[{'kind':outcome,'detail':reason}],output_prefix=captured.decode(errors='replace'))
            except BaseException as e:
                if process is not None:
                    try:teardown(process,process.pid,group)
                    except Exception as cleanup_error:base['events'].append({'kind':'cleanup-error','detail':str(cleanup_error)})
                base.update(status='nonqualified',outcome='cancelled' if isinstance(e,KeyboardInterrupt) else 'worker-failed',reason=str(e),seconds=time.monotonic()-started,job=str(job))
            finally:
                streams.close()
                if process is not None:
                    for pipe in [process.stdout,process.stderr]:pipe.close()
                if group:
                    try:group.close()
                    except Exception as e:base.update(status='nonqualified',complete=False,outcome='worker-failed',reason='Cgroup cleanup: '+str(e))
                if previous_subreaper is not None:
                    try:restore_subreaper(previous_subreaper)
                    except Exception as e:base.update(status='nonqualified',complete=False,outcome='worker-failed',reason='Parent-state restoration: '+str(e))
            base['seconds']=time.monotonic()-started
            if base['complete'] and base['seconds']>self.policy['run_seconds']:
                base.update(status='nonqualified',complete=False,outcome='timeout',reason='Whole-run deadline exceeded during final cleanup.')
            (job/'run-record.json').write_text(json.dumps(base,indent=2)+'\n')
            return base

"""Actual process-group limits; qualification bridge is a separate gate."""
from pathlib import Path
import copy
import json
import subprocess
import sys
import threading
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p06.supervisor import Supervisor,capabilities
sys.path.insert(0,str(BASE/'execution'));import support as s
source=s.read(BASE/'p01/request-fixture.json')['resource_policy'];controls=[];runs=[]
def run(name,code,seconds=2,output=8192,memory=268435456,cancel_after=None):
    policy=copy.deepcopy(source);policy.update(run_seconds=seconds,output_bytes=output,memory_bytes=memory)
    cancel=threading.Event()
    timer=threading.Timer(cancel_after,cancel.set) if cancel_after is not None else None
    if timer:timer.start()
    try:r=Supervisor(HERE/'control-runs',policy).run([sys.executable,'-c',code],cancel)
    finally:
        if timer:timer.cancel()
    s.write(HERE/(name+'-run.json'),r);runs.append(s.binding(HERE/(name+'-run.json')))
    s.require(not r['qualified_receipt'] and not r['application_authorized'],'generic worker emitted qualified receipt')
    if 'cleanup' in r:s.require(r['cleanup']['remaining_pids']==[],'unreaped group')
    return r
def check(name,condition):s.require(condition,'control failed '+name);controls.append({'name':name,'result':'pass'})
r=run('normal','print("completed")');check('normal-command-completed',r['complete'] and r['outcome']=='completed')
r=run('deadline','import time\nfor _ in range(8): time.sleep(.1)',seconds=.3);check('whole-run-timeout-across-short-stages',r['outcome']=='timeout' and not r['complete'])
r=run('output','import sys\nwhile True: sys.stdout.write("x"*65536);sys.stdout.flush()',output=1024);check('output-flood-refuses',r['outcome']=='output-limit' and len(r['output_prefix'].encode())<=1024)
r=run('cancel','import time,subprocess,sys\np=subprocess.Popen([sys.executable,"-c","import time;time.sleep(20)"])\ntime.sleep(20)',cancel_after=.25);check('cancellation-kills-and-reaps-descendants',r['outcome']=='cancelled' and len(r['observed_pids'])>=2)
r=run('forced','import os,signal\nos.kill(os.getpid(),signal.SIGKILL)');check('forced-worker-termination-nonqualified',r['outcome']=='worker-failed' and not r['complete'])
r=run('aggregate','import subprocess,sys,time\nx=bytearray(40*1024*1024)\np=subprocess.Popen([sys.executable,"-c","import time;x=bytearray(40*1024*1024);time.sleep(20)"])\ntime.sleep(20)',memory=75*1024*1024);check('actual-parent-child-advisory-aggregate-exhaustion',r['outcome']=='oom' and r['enforcement']=='advisory' and 'no kernel OOM' in r['reason'] and len(r['observed_pids'])>=2)
info=capabilities();s.write(HERE/'host-capabilities.json',info)
required=copy.deepcopy(source);required['memory_mode']='required'
if not info['required_memory_available']:
    r=Supervisor(HERE/'control-runs',required).run([sys.executable,'-c','raise Exception("must not launch")'])
    check('actual-unavailable-required-policy-refuses-before-launch',r['outcome']=='policy-unavailable' and r['enforcement']=='unavailable' and 'job' not in r)
else:
    # This host-specific control requires actual delegated cgroups. It never
    # treats a temporary directory as kernel enforcement.
    r=Supervisor(HERE/'control-runs',required,pids_max=64).run([sys.executable,'-c','print("required backend")'])
    check('actual-required-cgroup-command',r['complete'] and r['enforcement']=='cgroup-v2')
busy_policy=copy.deepcopy(source);busy_policy['run_seconds']=3
sup=Supervisor(HERE/'control-runs',busy_policy);answer=[]
worker=threading.Thread(target=lambda:answer.append(sup.run([sys.executable,'-c','import time;time.sleep(.8)'])));worker.start()
until=time.monotonic()+1
while not list((HERE/'control-runs').glob('job-*/go')) and time.monotonic()<until:time.sleep(.01)
time.sleep(.15)
busy=sup.run([sys.executable,'-c','print("second")']);worker.join()
check('simultaneous-expensive-job-refused',busy['status']=='refused' and 'already active' in busy['reason'] and answer[0]['complete'])
s.write(HERE/'supervisor-controls.json',{'result':'pass','controls':controls,'runs':runs,'qualification_bridge_complete':False,'hard_cgroup_memory_tested':info['required_memory_available'],'memory_boundary':'Actual parent/child RSS sampling stop in advisory mode; no hard cap or kernel OOM is claimed on an undelegated host.','authority_effect':'none'})
print('Supervisor controls passed: '+str(len(controls))+'; P06 qualification bridge remains incomplete')

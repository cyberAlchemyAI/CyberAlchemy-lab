"""R02/API14 parent guards with independently selected original-system worker."""
import ast
import fcntl
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime,timezone
import build_runtime as B

def main():
    here=B.HERE;api=B.BASE/'api-integration-v14';prefix=here/'method-native-namespace-0003'
    pin='aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240'
    profile='327d3c480168b0008597969e31e11e73f429370a226bd16370245e82ef78fb16'
    inputs=here/'method-native-system-historical-inputs-v2.json'
    value=B.load(inputs);input_pin=B.bind(inputs)['sha256']
    worker=here/'method_historical_worker_v2.py';B.need(B.bind(worker)==value['caller_binding'],'worker differs from independent selection')
    ast.parse(B.read(worker));ast.parse(B.read(Path(__file__)))
    interpreter=Path(value['system_runtime_environment']['interpreter'])
    B.need(interpreter==Path('/usr/bin/python3.14'),'unselected historical interpreter')
    lock=B.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/final-api-regression-0173-0190.execution.lock'
    fd=os.open(lock,os.O_RDWR|os.O_NOFOLLOW);started=datetime.now(timezone.utc).isoformat();entry=False;exit_guard=False;child=None;error=None
    try:
        fcntl.flock(fd,fcntl.LOCK_SH)
        guard=B.module('_method_system_R02_parent_guard',api/'guard.py');guard.verify(pin);B.exact(api/'contract-profile.json',profile);entry=True
        for row in value['files']+value['system_runtime_files']:B.need(B.bind(B.ROOT/row['path'])==row,'selected historical byte changed')
        argv=[str(interpreter),'-B',str(worker),'--api-directory',str(api),'--source-sha256',pin,'--profile-sha256',profile,
            '--historical-inputs',str(inputs),'--historical-inputs-sha256',input_pin,'--output-prefix',str(prefix)]
        run=subprocess.run(argv,capture_output=True,text=True,pass_fds=(fd,),env={**os.environ,'S02_INHERITED_SCOPE_FD':str(fd)})
        child={'argv':argv,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr}
        guard.verify(pin);B.exact(api/'contract-profile.json',profile)
        for row in value['files']+value['system_runtime_files']:B.need(B.bind(B.ROOT/row['path'])==row,'selected historical exit byte changed')
        exit_guard=True
    except Exception as exc:error={'type':type(exc).__name__,'message':str(exc)}
    finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
    good=error is None and entry and exit_guard and child and child['returncode']==0
    report={'schema_version':'lab-original-system-S01-parent-guard-proof/v1-candidate','result':'PASS-REHEARSAL' if good else 'FAIL',
        'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'caller_binding':B.bind(Path(__file__)),
        'historical_inputs_binding':B.bind(inputs),'actual_worker_subprocess':child,'error':error,
        'API14_full_R02_entry_guard':entry,'API14_full_R02_exit_guard':exit_guard,
        'independent_original_historical_inputs':len(value['files']),'independent_system_runtime_files':len(value['system_runtime_files']),
        'nested_shared_lock_acquisition':False,'same_inherited_actual_scope_descriptor':True,
        'worker_report_binding':B.bind(Path(str(prefix)+'.json')) if Path(str(prefix)+'.json').exists() else None,
        'original_descriptor_schema_unchanged':True,'API14_qualification_transferred':False,
        'fixture_only':True,'canonical_admissions':0,'actual_owner_outcome':None,'human_outcome':None,
        'authority_effect':'none','release_ready':False,'task_complete':False,'goal_complete':False}
    B.emit(here/'method-system-parent-proof-0001.json',report)
    print(json.dumps({'result':report['result'],'report_binding':B.bind(here/'method-system-parent-proof-0001.json'),'worker_returncode':child['returncode'] if child else None,'error':error}),flush=True)
    return 0 if good else 1

if __name__=='__main__':raise SystemExit(main())

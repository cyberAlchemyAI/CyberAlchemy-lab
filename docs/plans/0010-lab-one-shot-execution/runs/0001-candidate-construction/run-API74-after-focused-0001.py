"""Qualify original selected behavior only after actual current focused PASS."""
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
from pathlib import Path
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v74'
SOURCE='0920790bafbdc771167966ab092c2081062069ae28f9f85c712d0e3e0185c91f'
PROFILE='5d8fc977969f229a41aa5d05553da44efec43e0e6912880f1b60d3d25dafbce4'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def main():
    focused_path=API/'receipts/workflow-composition-focused-checks-0001.json'
    focused=load(focused_path)
    assert focused['result']=='PASS' and focused['actual_cases']==1 and focused['actual_public_calls']==5
    assert focused['source_sha256']==SOURCE and focused['profile_sha256']==PROFILE
    assert bind(API/'source-manifest.json')['sha256']==SOURCE
    assert bind(API/'contract-profile.json')['sha256']==PROFILE
    selections=[('workflow-full', [sys.executable,'-B',str(API/'checks_workflow_composition.py'),
        '--source-sha256',SOURCE,'--profile-sha256',PROFILE,'--scope','full'],
        API/'receipts/workflow-composition-full-checks-0001.json',3),
        ('machine-read-focused',[sys.executable,'-B',str(RUN/'qualify-API74-machine-read-0001.py')],
        RUN/'API74-machine-read-diagnosis-0001.json',1)]
    for name,command,report_path,expected in selections:
        assert not report_path.exists()
        started=datetime.now(timezone.utc).isoformat()
        print(json.dumps({'phase':'STARTING','selection':name,'expected_cases':expected}),flush=True)
        log=RUN/f'API74-{name}-driver-0001.log'
        with log.open('xb') as stream:completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
        value={'schema_version':'lab-child-process-terminal/v1-candidate','command':command,
            'actual_exit_code':completed.returncode,'started_at':started,
            'completed_at':datetime.now(timezone.utc).isoformat(),'expected_cases':expected,
            'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
            'producer_binding':bind(Path(__file__).resolve()),'log_binding':bind(log),
            'focused_prerequisite_binding':bind(focused_path),'authority_effect':'none',
            'actual_owner_outcome':None,'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
        if report_path.exists():
            report=load(report_path)
            value.update(report_binding=bind(report_path),result=report['result'],actual_cases=report['actual_cases'],
                failures=report['failures'],errors=report['errors'])
            if 'source_sha256' in report:assert report['source_sha256']==SOURCE and report['profile_sha256']==PROFILE
            for key in ('actual_public_calls','completed_Machine_public_replies','source_guarded_exit_completed',
                        'owned_fixture_cleanup_completed'):
                if key in report:value[key]=report[key]
        path=RUN/f'API74-{name}-terminal-0001.json'
        with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
        print(json.dumps({'phase':'TERMINAL','selection':name,'actual_exit_code':completed.returncode,
                         'terminal_binding':bind(path)}),flush=True)
        if completed.returncode!=0:return completed.returncode
        assert value['result']=='PASS' and value['actual_cases']==expected
    return 0
if __name__=='__main__':raise SystemExit(main())

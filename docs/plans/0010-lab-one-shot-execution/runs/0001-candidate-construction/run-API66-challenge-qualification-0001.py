"""One original focused run, then the seven-case suite only after actual PASS."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v66'
SOURCE='4f130de8d542dd128a7c30b0d9bc06fa5c60f36addbe8d16c9a8cfcce9588394'
PROFILE='6b67e512a5d42caf7b7d5326bb99fb5da766cffcdf8ca8cfc69a0335a76e026c'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as stream:json.dump(v,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    assert bind(API/'source-manifest.json')['sha256']==SOURCE and bind(API/'contract-profile.json')['sha256']==PROFILE
    for scope,expected in (('focused',1),('full',7)):
        report_path=API/f'receipts/challenge-{scope}-checks-0001.json';assert not report_path.exists()
        command=[sys.executable,'-B',str(API/'checks_challenge.py'),'--source-sha256',SOURCE,'--profile-sha256',PROFILE,'--scope',scope]
        started=datetime.now(timezone.utc).isoformat();print(json.dumps({'phase':'STARTING','scope':scope,'expected_cases':expected,'started_at':started}),flush=True)
        log=RUN/f'API66-challenge-{scope}-driver-0001.log'
        with log.open('xb') as stream:completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
        terminal={'schema_version':'lab-child-process-terminal/v1-candidate','command':command,'scope':scope,
            'actual_exit_code':completed.returncode,'source_binding':bind(API/'source-manifest.json'),
            'profile_binding':bind(API/'contract-profile.json'),'log_binding':bind(log),'producer_binding':bind(Path(__file__).resolve()),
            'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),'expected_cases':expected,
            'authority_effect':'none','actual_owner_outcome':None,'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
        if report_path.exists():
            report=json.loads(report_path.read_bytes())
            terminal.update(report_binding=bind(report_path),result=report['result'],actual_cases=report['actual_cases'],
                actual_public_calls=report['actual_public_calls'],failures=report['failures'],errors=report['errors'],
                full_selected_suite_completed=report['full_selected_suite_completed'],
                source_guarded_exit_completed=report['source_guarded_exit_completed'],
                owned_fixture_cleanup_completed=report['owned_fixture_cleanup_completed'])
        path=RUN/f'API66-challenge-{scope}-terminal-0001.json';emit(path,terminal)
        print(json.dumps({'phase':'TERMINAL','scope':scope,'actual_exit_code':completed.returncode,'terminal_binding':bind(path)}),flush=True)
        if completed.returncode!=0:return completed.returncode
        assert terminal['result']=='PASS' and terminal['actual_cases']==expected and terminal['full_selected_suite_completed']
    return 0
if __name__=='__main__':raise SystemExit(main())

"""Capture the actual child terminal and bounded selected workflow evidence."""
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
from pathlib import Path
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v72'
SOURCE='1e18a7d5a2c310ee200f3d4cf6c1f95cb50bb9fad6252028fdc5d29b5b684c24'
PROFILE='5bc5478c5109c636c8c0e3212e07eb7b49e612bf1914e1033301eb3329b7e704'
def bind(path):
    return {'path':path.relative_to(ROOT).as_posix(), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    assert bind(API/'source-manifest.json')['sha256']==SOURCE
    assert bind(API/'contract-profile.json')['sha256']==PROFILE
    report_path=API/'receipts/workflow-composition-focused-checks-0001.json'
    assert not report_path.exists()
    command=[sys.executable,'-B',str(API/'checks_workflow_composition.py'),
        '--source-sha256',SOURCE,'--profile-sha256',PROFILE,'--scope','focused']
    started=datetime.now(timezone.utc).isoformat()
    log=RUN/'API72-workflow-focused-driver-0001.log'
    with log.open('xb') as stream:
        completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
    value={'schema_version':'lab-child-process-terminal/v1-candidate',
        'command':command,'actual_exit_code':completed.returncode,
        'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'log_binding':bind(log),'producer_binding':bind(Path(__file__).resolve()),
        'authority_effect':'none','actual_owner_outcome':None,'whole_API_qualified':False,
        'task_complete':False,'goal_complete':False}
    if report_path.exists():
        report=json.loads(report_path.read_bytes())
        assert report['source_sha256']==SOURCE and report['profile_sha256']==PROFILE
        value.update(report_binding=bind(report_path),result=report['result'],
            actual_cases=report['actual_cases'],actual_public_calls=report['actual_public_calls'],
            failures=report['failures'],errors=report['errors'])
    path=RUN/'API72-workflow-focused-terminal-0001.json'
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'actual_exit_code':completed.returncode,'terminal_binding':bind(path)}),flush=True)
    return completed.returncode
if __name__=='__main__':raise SystemExit(main())

"""Capture the actual child terminal and bounded selected workflow evidence."""
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
from pathlib import Path
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v75'
SOURCE='35c97975fe0be4541d6a87f0881b60c11991746b8b3e661ccbbd81c34aaa4b20'
PROFILE='ad09f11a40f2c6f195a13b87889ce51817b6532670d2da0459ab48014eaf8c6c'
def bind(path):
    return {'path':path.relative_to(ROOT).as_posix(), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    assert bind(API/'source-manifest.json')['sha256']==SOURCE
    assert bind(API/'contract-profile.json')['sha256']==PROFILE
    report_path=API/'receipts/carrier-reference-full-checks-0001.json'
    assert not report_path.exists()
    command=[sys.executable,'-B',str(API/'checks_carrier_references.py'),
        '--source-sha256',SOURCE,'--profile-sha256',PROFILE,'--scope','full']
    started=datetime.now(timezone.utc).isoformat()
    log=RUN/'API75-reference-full-driver-0001.log'
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
    path=RUN/'API75-reference-full-terminal-0001.json'
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'actual_exit_code':completed.returncode,'terminal_binding':bind(path)}),flush=True)
    return completed.returncode
if __name__=='__main__':raise SystemExit(main())

"""Capture the actual owned Source6 producer terminal without restarting it."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
SOURCE=ROOT/'product/lab/release-candidates/v1/interface/current-participation-v6'
PIN='074db4f0774fd14606e7f6940a8d8d5996b0fb031f99f180c518b6946f38abf0'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    assert bind(SOURCE/'source-manifest.json')['sha256']==PIN and not (SOURCE/'packages').exists()
    command=[sys.executable,'-B',str(SOURCE/'produce.py'),'--source-sha256',PIN]
    started=datetime.now(timezone.utc).isoformat();log=RUN/'current-participation-build-0006.log'
    print(json.dumps({'phase':'STARTING','source_binding':bind(SOURCE/'source-manifest.json')}),flush=True)
    with log.open('xb') as stream:completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
    value={'schema_version':'lab-child-process-terminal/v1-candidate','actual_exit_code':completed.returncode,
        'command':command,'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),
        'source_binding':bind(SOURCE/'source-manifest.json'),'producer_binding':bind(Path(__file__).resolve()),
        'log_binding':bind(log),'authority_effect':'none','actual_owner_outcome':None,
        'current_Agent_qualified':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    report=SOURCE/'packages/0001/build-result.json'
    if report.exists():
        result=json.loads(report.read_bytes());value.update(result=result['result'],report_binding=bind(report),
            signed_transactions=result['signed_transactions'],actual_original_targets=result['actual_original_targets'],
            owned_store_and_key_removed=result['owned_store_and_key_removed'])
    package=SOURCE/'packages/0001/manifest.json'
    if package.exists():value['package_binding']=bind(package)
    output=RUN/'current-participation-build-terminal-0006.json'
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'actual_exit_code':completed.returncode,'terminal_binding':bind(output)}),flush=True)
    return completed.returncode


if __name__=='__main__':raise SystemExit(main())

"""Capture the actual frozen new-source producer and owned cleanup outcome."""
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
SOURCE=ROOT/'product/lab/release-candidates/v1/interface/current-participation-v5'
PIN='dc0462ce29d24bf571b56c0c0eeafad0511812a8464ce66e52914671256e7cb4'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    assert bind(SOURCE/'source-manifest.json')['sha256']==PIN and not (SOURCE/'packages').exists()
    command=[sys.executable,'-B',str(SOURCE/'produce.py'),'--source-sha256',PIN]
    started=datetime.now(timezone.utc).isoformat();log=RUN/'current-participation-build-0005.log'
    with log.open('xb') as stream:completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
    value={'schema_version':'lab-child-process-terminal/v1-candidate','actual_exit_code':completed.returncode,
        'command':command,'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),
        'source_binding':bind(SOURCE/'source-manifest.json'),'producer_binding':bind(Path(__file__).resolve()),
        'log_binding':bind(log),'authority_effect':'none','actual_owner_outcome':None,
        'current_Agent_qualified':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    report=SOURCE/'packages/0001/build-result.json'
    if report.exists():
        observed=json.loads(report.read_bytes());value.update(report_binding=bind(report),result=observed['result'],
            signed_transactions=observed['signed_transactions'],canonical_effects_applied=observed['canonical_effects_applied'],
            owned_store_and_key_removed=observed['owned_store_and_key_removed'])
    package=SOURCE/'packages/0001/manifest.json'
    if package.exists():value['package_binding']=bind(package)
    path=RUN/'current-participation-build-terminal-0005.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'actual_exit_code':completed.returncode,'terminal_binding':bind(path)}),flush=True)
    return completed.returncode
if __name__=='__main__':raise SystemExit(main())

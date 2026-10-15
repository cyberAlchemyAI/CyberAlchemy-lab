"""Capture actual native mapping of the independently qualified signed source."""
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
HERE=ROOT/'product/lab/release-candidates/v1/interface/current-mapped-context-v4'
PIN='38e24b3517ef1868c57fc21e58e300e578187303a888dd9b22ff20e086d3317b'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert bind(HERE/'source-manifest.json')['sha256']==PIN
    assert not (HERE/'receipts/checks.json').exists()
    command=[sys.executable,'-B',str(HERE/'run.py'),'checks','--source-sha256',PIN,'--package-sha256','61eba56461293d8e056b71e2066d1ceec40aab633d8a4caf3ddaa550c57b981e']
    started=datetime.now(timezone.utc).isoformat();log=RUN/'current-mapping-checks-0004.log'
    with log.open('xb') as stream:completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
    value={'schema_version':'lab-child-process-terminal/v1-candidate','command':command,'actual_exit_code':completed.returncode,
        'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),'source_binding':bind(HERE/'source-manifest.json'),
        'producer_binding':bind(Path(__file__).resolve()),'log_binding':bind(log),'authority_effect':'none','actual_owner_outcome':None,
        'current_Agent_qualified':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    report=HERE/'receipts/checks.json';package=HERE/'packages/0001/manifest.json'
    if report.exists():value['report_binding']=bind(report)
    if package.exists():value['package_binding']=bind(package)
    path=RUN/'current-mapping-checks-terminal-0004.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'actual_exit_code':completed.returncode,'terminal_binding':bind(path)}),flush=True)
    return completed.returncode
if __name__=='__main__':raise SystemExit(main())

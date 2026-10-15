"""Capture independent signed original-body and same-cut adapter observations."""
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    for kind,script,source_file,observation,pin in [('mapping','audit-R03-current-mapping-0005.py','current-mapping-audit-source-0005.json','current-mapping-independent-observations-0005.json','4c42b67f623851c9cfe42dbfe71bab255e2574853434d016fea1d7540e155356')]:
        assert bind(RUN/source_file)['sha256']==pin and not (RUN/observation).exists()
        command=[sys.executable,'-B',str(RUN/script),'--source-sha256',pin]
        started=datetime.now(timezone.utc).isoformat();log=RUN/f'current-source-{kind}-audit-0005.log'
        print(json.dumps({'phase':'STARTING','audit':kind}),flush=True)
        with log.open('xb') as stream:completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
        value={'schema_version':'lab-child-process-terminal/v1-candidate','command':command,
            'actual_exit_code':completed.returncode,'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),
            'producer_binding':bind(Path(__file__).resolve()),'log_binding':bind(log),'audit_source_binding':bind(RUN/source_file),
            'authority_effect':'none','actual_owner_outcome':None,'current_Agent_qualified':False,
            'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
        report_path=RUN/observation
        if report_path.exists():
            observed=json.loads(report_path.read_bytes());value.update(result=observed['result'],checks=observed['checks'],observation_binding=bind(report_path))
        path=RUN/f'current-source-{kind}-audit-terminal-0005.json'
        with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
        print(json.dumps({'phase':'TERMINAL','audit':kind,'actual_exit_code':completed.returncode,'terminal_binding':bind(path)}),flush=True)
        if completed.returncode!=0:return completed.returncode
        assert value['result']=='PASS'
    return 0
if __name__=='__main__':raise SystemExit(main())

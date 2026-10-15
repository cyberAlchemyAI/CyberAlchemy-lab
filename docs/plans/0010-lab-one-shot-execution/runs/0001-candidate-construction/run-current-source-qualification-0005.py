"""Capture sequential actual source and adapter qualification terminals."""
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
SOURCE=BASE/'current-participation-v5';ADAPTER=BASE/'current-source-adapter-v4'
SOURCE_PIN='dc0462ce29d24bf571b56c0c0eeafad0511812a8464ce66e52914671256e7cb4'
PACKAGE_PIN='8c34a37e1dfa185fc21f323aa08d99c4f097b413c3e0fcf90c0da6d98c731aaf'
ADAPTER_PIN='be0e1857cf667100ea2dd9c6b115d11032f28fbfdfba4e9234d94aff84f19fee'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert bind(SOURCE/'source-manifest.json')['sha256']==SOURCE_PIN
    assert bind(SOURCE/'packages/0001/manifest.json')['sha256']==PACKAGE_PIN
    assert bind(ADAPTER/'source-manifest.json')['sha256']==ADAPTER_PIN
    for name,command,report_path in [
        ('source',[sys.executable,'-B',str(SOURCE/'checks.py'),'--source-sha256',SOURCE_PIN,
                   '--package-sha256',PACKAGE_PIN,'--checks-source-sha256',SOURCE_PIN],SOURCE/'receipts/checks-0001.json'),
        ('adapter',[sys.executable,'-B',str(ADAPTER/'run_checks.py'),'--source-sha256',ADAPTER_PIN],ADAPTER/'checks-result-0001.json')]:
        assert not report_path.exists()
        started=datetime.now(timezone.utc).isoformat();log=RUN/f'current-participation-{name}-checks-0005.log'
        print(json.dumps({'phase':'STARTING','selection':name,'expected_tests':20}),flush=True)
        with log.open('xb') as stream:completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
        value={'schema_version':'lab-child-process-terminal/v1-candidate','command':command,
            'actual_exit_code':completed.returncode,'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),
            'producer_binding':bind(Path(__file__).resolve()),'log_binding':bind(log),
            'source_binding':bind(SOURCE/'source-manifest.json'),'package_binding':bind(SOURCE/'packages/0001/manifest.json'),
            'adapter_source_binding':bind(ADAPTER/'source-manifest.json'),'authority_effect':'none','actual_owner_outcome':None,
            'current_Agent_qualified':False,'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
        if report_path.exists():
            report=json.loads(report_path.read_bytes());value.update(report_binding=bind(report_path),
                result=report['result'],tests_run=report['tests_run'],failures=report.get('failures'),errors=report.get('errors'))
        path=RUN/f'current-participation-{name}-checks-terminal-0005.json'
        with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
        print(json.dumps({'phase':'TERMINAL','selection':name,'actual_exit_code':completed.returncode,'terminal_binding':bind(path)}),flush=True)
        if completed.returncode!=0:return completed.returncode
        assert value['result']=='PASS' and value['tests_run']==20
    return 0
if __name__=='__main__':raise SystemExit(main())

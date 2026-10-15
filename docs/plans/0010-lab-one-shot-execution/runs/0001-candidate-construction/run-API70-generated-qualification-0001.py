"""Continue only after actual focused PASS; preserve each selected process result."""
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v70'
SOURCE='14ab42cb56cd2b0004fc95cea06369eacc4a7d6653cea9ffb019fd887e72b105'
PROFILE='707d2946129a948baee35f36aad2144344cc94d79044d7122605d61400d4cc78'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as stream:json.dump(v,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    assert bind(API/'source-manifest.json')['sha256']==SOURCE and bind(API/'contract-profile.json')['sha256']==PROFILE
    focused=json.loads((API/'receipts/generated-focused-checks-0001.json').read_bytes())
    assert focused['result']=='PASS' and focused['actual_cases']==1 and focused['actual_public_calls']==3
    assert focused['source_sha256']==SOURCE and focused['profile_sha256']==PROFILE
    for name,script,report_name,expected in (
        ('generated-full','checks_generated_candidate.py','generated-full-checks-0001.json',5),
        ('challenge-full','checks_challenge.py','challenge-full-checks-0001.json',7)):
        report_path=API/'receipts'/report_name;assert not report_path.exists()
        command=[sys.executable,'-B',str(API/script),'--source-sha256',SOURCE,'--profile-sha256',PROFILE,'--scope','full']
        started=datetime.now(timezone.utc).isoformat();print(json.dumps({'phase':'STARTING','scope':name,'expected_cases':expected,'started_at':started}),flush=True)
        log=RUN/f'API70-{name}-driver-0001.log'
        with log.open('xb') as stream:completed=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT)
        terminal={'schema_version':'lab-child-process-terminal/v1-candidate','command':command,'scope':name,
            'actual_exit_code':completed.returncode,'source_binding':bind(API/'source-manifest.json'),
            'profile_binding':bind(API/'contract-profile.json'),'log_binding':bind(log),'producer_binding':bind(Path(__file__).resolve()),
            'focused_prerequisite_binding':bind(API/'receipts/generated-focused-checks-0001.json'),
            'started_at':started,'completed_at':datetime.now(timezone.utc).isoformat(),'expected_cases':expected,
            'authority_effect':'none','actual_owner_outcome':None,'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
        if report_path.exists():
            report=json.loads(report_path.read_bytes())
            assert report['source_sha256']==SOURCE and report['profile_sha256']==PROFILE
            terminal.update(report_binding=bind(report_path),result=report['result'],actual_cases=report['actual_cases'],
                actual_public_calls=report['actual_public_calls'],failures=report['failures'],errors=report['errors'],
                full_selected_suite_completed=report['full_selected_suite_completed'],
                source_guarded_exit_completed=report['source_guarded_exit_completed'],
                owned_fixture_cleanup_completed=report['owned_fixture_cleanup_completed'])
        path=RUN/f'API70-{name}-terminal-0001.json';emit(path,terminal)
        print(json.dumps({'phase':'TERMINAL','scope':name,'actual_exit_code':completed.returncode,'terminal_binding':bind(path)}),flush=True)
        if completed.returncode!=0:return completed.returncode
        assert terminal['result']=='PASS' and terminal['actual_cases']==expected and terminal['full_selected_suite_completed']
    return 0
if __name__=='__main__':raise SystemExit(main())

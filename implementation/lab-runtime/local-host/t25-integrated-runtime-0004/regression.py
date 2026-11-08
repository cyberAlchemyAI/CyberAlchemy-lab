"""Serial fresh-process accounting for the maintained installed method inventory."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
P=sys.modules.get('cal_installed_runtime_selection_v1')
if P is None or Path(P.__file__)!=HERE/'installed_selection.py':raise ValueError('regression requires selected native bootstrap')
P.require_runtime_ready()
if P.root()!=ROOT:raise ValueError('regression and installed selection root differ')
API=ROOT/P.current().package['entrypoint']['api_directory']
INVENTORY=ROOT/'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
WORKER=HERE/'regression_worker.py'
SOURCE_SHA=P.binding('api.source')['sha256']
PROFILE_SHA=P.binding('api.profile')['sha256']
INVENTORY_SHA='bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3'
INSTALL=Path(P.value('native.root'))
WORK=ROOT.parent/'.cal-runtime/regression'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def utc():
    return datetime.now(timezone.utc).isoformat()

def checked():
    P.guard()
    for path,digest in ((API/'source-manifest.json',SOURCE_SHA),(API/'contract-profile.json',PROFILE_SHA),(INVENTORY,INVENTORY_SHA)):
        if not path.is_file() or path.is_symlink() or sha(path)!=digest:raise ValueError('selected regression byte differs: '+str(path))
    package=P.current().package
    for path in (Path(__file__),WORKER,INVENTORY):
        rows=[r for r in package['members'] if r['path']==path.relative_to(ROOT).as_posix()]
        if len(rows)!=1 or sha(path)!=rows[0]['sha256']:raise ValueError('regression helper differs from independently selected package')
    proof=P.process_proof()
    if not proof['all_executable_maps_selected']:raise ValueError('regression actual native maps differ')
    buckets=json.loads(INVENTORY.read_bytes())['buckets']
    ids=[i for methods in buckets.values() for i in methods]
    if len(buckets)!=21 or len(ids)!=len(set(ids)) or len(ids)!=345:raise ValueError('maintained inventory differs')
    return buckets

def command(bucket,run_id,worker_sha):
    # sys.executable is the independently attested static launcher. Its child
    # re-verifies all 1010 bytes, bootstrap, public package and private controls.
    return [sys.executable,'-B',str(WORKER),'--bucket',bucket,'--run-id',run_id,'--runner-sha256',worker_sha]

def run_owned_worker(argv, *, output, cwd, environment, timeout):
    """A timed-out test owns its new process group, including native children."""
    child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=output,
                           stderr=subprocess.STDOUT,cwd=cwd,env=environment,
                           start_new_session=True)
    def terminate_owned_group():
        try:os.killpg(child.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        try:child.wait(timeout=3)
        except subprocess.TimeoutExpired:pass
        # The group may still contain a child after its leader has exited.
        try:os.killpg(child.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        child.wait()
    try:
        code=child.wait(timeout=timeout)
        # A zero-exit worker can still leave a descendant in its owned process
        # group. Drain that group before accepting its terminal receipt.
        terminate_owned_group()
        return code,False
    except subprocess.TimeoutExpired:
        terminate_owned_group()
        return child.returncode,True
    except BaseException:
        terminate_owned_group()
        raise

def bucket_pass(result, ids, exit_code, timed_out):
    """Method PASS rows cannot erase fixture, process, or exit-guard failures."""
    return (result.get('result')=='PASS' and exit_code==0 and not timed_out
            and result.get('tests_run')==len(ids)
            and result.get('exact_case_set') is True
            and result.get('all_methods_executed') is True
            and result.get('entry_guard_passed') is True
            and result.get('exit_guard_passed') is True
            and not result.get('fixture_errors')
            and result.get('execution_error') is None
            and [row.get('id') for row in result.get('cases',[])]==ids
            and all(row.get('executed') is True and row.get('result')=='PASS'
                    for row in result['cases']))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--only-bucket',help='One complete inventory class; a bounded focus never qualifies the full suite')
    parser.add_argument('--timeout-seconds',type=int,default=3600)
    args=parser.parse_args()
    if not re.fullmatch('[a-z][a-z0-9-]{0,31}',args.run_id) or not args.workers == 1 or not 60 <= args.timeout_seconds <= 14400:
        raise ValueError('invalid bounded regression parameters')
    os.umask(0o077)
    buckets=checked(); full_suite=args.only_bucket is None
    if args.only_bucket is not None:
        if args.only_bucket not in buckets:raise ValueError('unknown whole-class focus')
        buckets={args.only_bucket:buckets[args.only_bucket]}
    selected_count=sum(len(ids) for ids in buckets.values()); bucket_count=len(buckets)
    worker_sha=sha(WORKER)
    work=WORK/args.run_id
    work.mkdir(mode=0o700,parents=True,exist_ok=False)
    started=utc()
    selection={'schema_version':'lab-installed-maintained-serial-selection/v1',
               'api_source_sha256':SOURCE_SHA,'api_profile_sha256':PROFILE_SHA,
               'inventory_sha256':INVENTORY_SHA,'worker_sha256':worker_sha,
               'coordinator_sha256':sha(__file__), 'installation_receipt_sha256':sha(INSTALL/'installation.json'),
               'package_manifest_sha256':P.current().package_pin,'workers':args.workers,'timeout_seconds':args.timeout_seconds,
               'selected_buckets':bucket_count,'selected_methods':selected_count,'full_suite_selected':full_suite,'authority_effect':'none'}
    (work/'SELECTION.json').write_text(json.dumps(selection,sort_keys=True,indent=2)+'\n')
    def one(position,bucket,ids):
        safe=bucket.replace(':','-').replace('.','-')
        log=work/(safe+'-LOG.txt')
        result_path=work/(safe+'-RESULT.json')
        begin=utc()
        try:
            checked()
            with log.open('xb') as output:
                environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
                code,timed_out=run_owned_worker(command(bucket,args.run_id,worker_sha),
                                     output=output,cwd=ROOT,environment=environment,
                                     timeout=args.timeout_seconds)
        except BaseException as error:
            code=None;timed_out=False
            return {'bucket':bucket,'position':position,'status':'SELECTION-ERROR',
                    'cause':str(error),'cases':[{'id':i,'result':'NOT-RUN-SELECTION-ERROR','executed':False} for i in ids]}
        if result_path.is_file():
            try:
                result=json.loads(result_path.read_bytes())
                if (result['schema_version'] != 'lab-installed-maintained-bucket/v1' or
                    result['source_sha256'] != SOURCE_SHA or result['profile_sha256'] != PROFILE_SHA or
                    result['inventory_sha256'] != INVENTORY_SHA or result['runner_sha256'] != worker_sha or
                    result['selected_ids'] != ids or [r['id'] for r in result['cases']] != ids or
                    result['bucket'] != bucket or result['run_id'] != args.run_id):
                    raise ValueError('worker selection or exact method set differs')
                if sha(work/(safe+'-EVENTS.jsonl'))!=result['events_sha256']:
                    raise ValueError('worker event log digest differs')
                accepted_pass=bucket_pass(result,ids,code,timed_out)
                return {'bucket':bucket,'position':position,'status':'PASS' if accepted_pass else 'FAIL',
                        'tests_run':result['tests_run'],'fixture_errors':result['fixture_errors'],
                        'execution_error':result['execution_error'], 'entry_guard_passed':result['entry_guard_passed'],
                        'exit_guard_passed':result['exit_guard_passed'],'cases':result['cases'],
                        'worker_result_sha256':sha(result_path),'log_sha256':sha(log),
                        'exit_code':code,'timed_out':timed_out,'started_at_utc':begin,'ended_at_utc':utc()}
            except BaseException as error:
                cause='WORKER-RESULT-REFUSED: '+str(error)
        else:
            cause='WORKER-TIMEOUT' if timed_out else 'WORKER-NO-RESULT'
        return {'bucket':bucket,'position':position,'status':cause,'exit_code':code,
                'timed_out':timed_out,'log_sha256':sha(log) if log.exists() else None,
                'cases':[{'id':i,'result':cause,'executed':False} for i in ids],
                'started_at_utc':begin,'ended_at_utc':utc()}
    rows=[]
    stopped=False
    for n,(bucket,ids) in enumerate(buckets.items(),1):
        if stopped:
            row={'bucket':bucket,'position':n,'status':'NOT-RUN-AFTER-FAILURE',
                 'cases':[{'id':i,'result':'NOT-RUN-AFTER-FAILURE','executed':False} for i in ids]}
        else:
            row=one(n,bucket,ids)
            stopped=row['status']!='PASS'
        rows.append(row)
        (work/'PROGRESS.jsonl').open('a').write(json.dumps({'at_utc':utc(),'bucket':row['bucket'],
             'status':row['status'],'tests_run':row.get('tests_run',0),
             'executed':sum(c['executed'] for c in row['cases'])},sort_keys=True)+'\n')
        print(json.dumps({'bucket':row['bucket'],'status':row['status'],
                          'executed':sum(c['executed'] for c in row['cases'])}),flush=True)
    rows.sort(key=lambda x:x['position'])
    cases=[case for row in rows for case in row['cases']]
    selected=[identity for ids in buckets.values() for identity in ids]
    exact=[case['id'] for case in cases]==selected
    try: checked(); selection_unchanged=sha(WORKER)==worker_sha and sha(__file__)==selection['coordinator_sha256']
    except BaseException: selection_unchanged=False
    receipt={'schema_version':'lab-installed-maintained-serial-regression/v1',
             'run_id':args.run_id,'source_sha256':SOURCE_SHA,'profile_sha256':PROFILE_SHA,
             'inventory_sha256':INVENTORY_SHA,'worker_sha256':worker_sha,
             'selection_sha256':sha(work/'SELECTION.json'),'started_at_utc':started,'ended_at_utc':utc(),
             'selected_method_count':selected_count,'selected_bucket_count':bucket_count,'full_suite_selected':full_suite,'max_concurrency':args.workers,
             'exact_case_set':exact,'selection_unchanged':selection_unchanged,
             'executed_method_count':sum(c['executed'] for c in cases),
             'pass_method_count':sum(c['executed'] and c['result']=='PASS' for c in cases),
             'bucket_results':rows,'result':'PASS' if exact and selection_unchanged and
             all(row['status']=='PASS' for row in rows) and all(c['executed'] and c['result']=='PASS' for c in cases) else 'INCOMPLETE-OR-FAIL',
             't16_qualified':False,'authority_effect':'none',
             'claim_ceiling':'Actual selected installed API maintained suite; full task acceptance also requires operation, crash, privacy and independent review proofs.'}
    (work/'REGRESSION-RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'result':receipt['result'],'selected':selected_count,'executed':receipt['executed_method_count'],
                      'passed':receipt['pass_method_count'],'receipt':str(work/'REGRESSION-RESULT.json')}),flush=True)
    return 0 if receipt['result']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())

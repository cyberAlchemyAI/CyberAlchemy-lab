"""Bounded fresh-process accounting for the inherited API62 method inventory."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v62-t16-abi423-alias-0001'
INVENTORY = ROOT / 'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
INSTALL = Path('/tmp/cal-T03-native-install-20261023/0001')
WORKER = HERE / 'run_bucket_api62.py'
SOURCE_SHA = '9c39d58572139a731d610bb0cf174655892106b805985567762c2041a98b94be'
PROFILE_SHA = 'c98076fd86b3fced1d7b356017efd234c0205b62c7f357a28419d709d56e5258'
INVENTORY_SHA = 'bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def utc():
    return datetime.now(timezone.utc).isoformat()

def checked():
    for path, digest in ((API/'source-manifest.json', SOURCE_SHA),
                         (API/'contract-profile.json', PROFILE_SHA),
                         (INVENTORY, INVENTORY_SHA),
                         (INSTALL/'bin/lab-context-native-reader', NATIVE_SHA)):
        if not path.is_file() or path.is_symlink() or sha(path) != digest:
            raise ValueError('selected byte unavailable or differs: '+str(path))
    install = json.loads((INSTALL/'installation.json').read_bytes())
    if install['selection_sha256'] != '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835' or install['file_count'] != 1010:
        raise ValueError('selected installed closure differs')
    buckets = json.loads(INVENTORY.read_bytes())['buckets']
    ids = [identity for methods in buckets.values() for identity in methods]
    if len(buckets) != 21 or len(ids) != len(set(ids)) or len(ids) != 345:
        raise ValueError('inherited inventory differs')
    return buckets

def command(bucket, run_id, worker_sha):
    paths = [str(INSTALL/'deps'), str(API.parent), str(ROOT)]
    bootstrap = (
        'import importlib.metadata,json,platform,runpy,sys; '
        'sys.path[:0]=json.loads(sys.argv[1]); '
        'assert (platform.python_version(),importlib.metadata.version("jsonschema"),'
        'importlib.metadata.version("cryptography"))==("3.14.4","4.23.0","46.0.5"); '
        'target=sys.argv[2]; sys.argv=[target,*sys.argv[3:]]; '
        'runpy.run_path(target,run_name="__main__")')
    return [str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'), '--inhibit-cache',
            '--library-path', str(INSTALL/'lib/abi'), str(INSTALL/'bin/python'),
            '-I','-X','utf8','-B','-S','-c',bootstrap,json.dumps(paths),str(WORKER),
            '--bucket',bucket,'--run-id',run_id,'--runner-sha256',worker_sha]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--timeout-seconds',type=int,default=3600)
    args=parser.parse_args()
    if not re.fullmatch('[a-z][a-z0-9-]{0,31}',args.run_id) or not args.workers == 1 or not 60 <= args.timeout_seconds <= 14400:
        raise ValueError('invalid bounded regression parameters')
    os.umask(0o077)
    buckets=checked(); worker_sha=sha(WORKER)
    work=HERE/'working'/args.run_id
    work.mkdir(mode=0o700,parents=True,exist_ok=False)
    started=utc()
    selection={'schema_version':'lab-T16-API62-parallel-regression-selection/v1-candidate',
               'api_source_sha256':SOURCE_SHA,'api_profile_sha256':PROFILE_SHA,
               'inventory_sha256':INVENTORY_SHA,'worker_sha256':worker_sha,
               'coordinator_sha256':sha(__file__), 'installation_receipt_sha256':sha(INSTALL/'installation.json'),
               'native_sha256':NATIVE_SHA,'workers':args.workers,'timeout_seconds':args.timeout_seconds,
               'selected_buckets':21,'selected_methods':345,'authority_effect':'none'}
    (work/'SELECTION.json').write_text(json.dumps(selection,sort_keys=True,indent=2)+'\n')
    def one(position,bucket,ids):
        safe=bucket.replace(':','-').replace('.','-')
        log=work/(safe+'-LOG.txt')
        result_path=work/(safe+'-RESULT.json')
        begin=utc()
        try:
            checked()
            with log.open('xb') as output:
                child=subprocess.run(command(bucket,args.run_id,worker_sha),stdin=subprocess.DEVNULL,
                                     stdout=output,stderr=subprocess.STDOUT,cwd=ROOT,
                                     timeout=args.timeout_seconds,check=False)
            code=child.returncode; timed_out=False
        except subprocess.TimeoutExpired:
            code=None;timed_out=True
        except BaseException as error:
            code=None;timed_out=False
            return {'bucket':bucket,'position':position,'status':'SELECTION-ERROR',
                    'cause':str(error),'cases':[{'id':i,'result':'NOT-RUN-SELECTION-ERROR','executed':False} for i in ids]}
        if result_path.is_file():
            try:
                result=json.loads(result_path.read_bytes())
                if (result['schema_version'] != 'lab-t16-api62-parallel-bucket/v1' or
                    result['source_sha256'] != SOURCE_SHA or result['profile_sha256'] != PROFILE_SHA or
                    result['inventory_sha256'] != INVENTORY_SHA or result['runner_sha256'] != worker_sha or
                    result['selected_ids'] != ids or [r['id'] for r in result['cases']] != ids or
                    result['bucket'] != bucket or result['run_id'] != args.run_id):
                    raise ValueError('worker selection or exact method set differs')
                return {'bucket':bucket,'position':position,'status':result['result'],
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
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(one,n,bucket,ids):n for n,(bucket,ids) in enumerate(buckets.items(),1)}
        for future in as_completed(futures):
            row=future.result(); rows.append(row)
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
    receipt={'schema_version':'lab-T16-API62-parallel-inherited-regression/v1-candidate',
             'run_id':args.run_id,'source_sha256':SOURCE_SHA,'profile_sha256':PROFILE_SHA,
             'inventory_sha256':INVENTORY_SHA,'worker_sha256':worker_sha,
             'selection_sha256':sha(work/'SELECTION.json'),'started_at_utc':started,'ended_at_utc':utc(),
             'selected_method_count':345,'selected_bucket_count':21,'max_concurrency':args.workers,
             'exact_case_set':exact,'selection_unchanged':selection_unchanged,
             'executed_method_count':sum(c['executed'] for c in cases),
             'pass_method_count':sum(c['executed'] and c['result']=='PASS' for c in cases),
             'bucket_results':rows,'result':'PASS' if exact and selection_unchanged and
             all(c['executed'] and c['result']=='PASS' for c in cases) else 'INCOMPLETE-OR-FAIL',
             't16_qualified':False,'authority_effect':'none',
             'claim_ceiling':'Local API62 inherited regression only; historical locator and current family scope require separate qualification.'}
    (work/'REGRESSION-RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'result':receipt['result'],'selected':345,'executed':receipt['executed_method_count'],
                      'passed':receipt['pass_method_count'],'receipt':str(work/'REGRESSION-RESULT.json')}),flush=True)
    return 0 if receipt['result']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())

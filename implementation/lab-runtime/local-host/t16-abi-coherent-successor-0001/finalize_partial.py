"""Account for an intentionally stopped known-blocker API60 regression run."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
RUN=HERE/'working/api60-first-20261023'
INVENTORY=ROOT/'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(INVENTORY)!='bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3':
    raise ValueError('inherited method inventory differs')
buckets=json.loads(INVENTORY.read_bytes())['buckets']
selection=json.loads((RUN/'SELECTION.json').read_bytes())
rows=[]
for bucket,ids in buckets.items():
    safe=bucket.replace(':','-').replace('.','-')
    result_path=RUN/(safe+'-RESULT.json')
    log=RUN/(safe+'-LOG.txt')
    if result_path.is_file():
        result=json.loads(result_path.read_bytes())
        if result['selected_ids']!=ids or [r['id'] for r in result['cases']]!=ids or result['source_sha256']!=selection['api_source_sha256']:
            raise ValueError('selected worker result differs')
        rows.append({'bucket':bucket,'status':result['result'],'method_count':len(ids),
                     'tests_run':result['tests_run'],'fixture_errors':result['fixture_errors'],
                     'cases':result['cases'],'worker_result_sha256':sha(result_path),
                     'log_sha256':sha(log) if log.is_file() else None})
    else:
        status='INTERRUPTED-BY-BOUNDED-STOP' if log.is_file() else 'NOT-RUN-KNOWN-SETUP-BLOCKER'
        rows.append({'bucket':bucket,'status':status,'method_count':len(ids),'tests_run':0,
                     'cases':[{'id':identity,'result':status,'executed':False} for identity in ids],
                     'log_sha256':sha(log) if log.is_file() else None})
cases=[case for row in rows for case in row['cases']]
expected=[identity for ids in buckets.values() for identity in ids]
if [case['id'] for case in cases]!=expected or len(expected)!=345:
    raise ValueError('partial method ledger does not account for exact 345 IDs')
receipt={'schema_version':'lab-T16-API60-intentionally-stopped-regression/v1-candidate',
         'run_id':'api60-first-20261023','selected_source_sha256':selection['api_source_sha256'],
         'selected_profile_sha256':selection['api_profile_sha256'],
         'selection_sha256':sha(RUN/'SELECTION.json'),'inventory_sha256':sha(INVENTORY),
         'selected_bucket_count':21,'selected_method_count':345,
         'actual_executed_method_count':sum(c['executed'] for c in cases),
         'actual_pass_method_count':sum(c['executed'] and c['result']=='PASS' for c in cases),
         'terminal_accounting_count':len(cases),'bucket_results':rows,
         'result':'INCOMPLETE-KNOWN-LOCATOR-SETUP-BLOCKER','t16_qualified':False,
         'authority_effect':'none','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
         'stop_reason':'Owner stopped broad execution after exact historical setup failure was reproduced; fresh selected mapper/Context/API locator rebind is required before a 345-method retry.',
         'claim_ceiling':'An explicit partial ledger; unexecuted methods are not test failures or passes.'}
target=RUN/'PARTIAL-LEDGER.json'
with target.open('x') as output:
    json.dump(receipt,output,indent=2,sort_keys=True);output.write('\n')
print(json.dumps({'receipt':str(target),'sha256':sha(target),
                  'actual_executed':receipt['actual_executed_method_count'],
                  'accounted':receipt['terminal_accounting_count'],
                  'bucket_counts':{s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}},sort_keys=True))

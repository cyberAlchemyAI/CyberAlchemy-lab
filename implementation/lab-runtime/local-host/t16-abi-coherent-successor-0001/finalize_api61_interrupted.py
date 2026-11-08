"""Account for exact inherited methods after stopping an unsafe parallel sample."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
RUN=HERE/'working/api61-full-20261023'
INVENTORY=ROOT/'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sha(INVENTORY)!='bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3':
    raise ValueError('inherited inventory differs')
selection=json.loads((RUN/'SELECTION.json').read_bytes())
if selection['api_source_sha256']!='84435a57c990a1d85504cf844a257e6dc3607c81519d368c828449ac8106ffc4':
    raise ValueError('selected API61 differs')
buckets=json.loads(INVENTORY.read_bytes())['buckets'];rows=[]
for bucket,ids in buckets.items():
    safe=bucket.replace(':','-').replace('.','-')
    events=RUN/(safe+'-EVENTS.jsonl');log=RUN/(safe+'-LOG.txt')
    found={};started=set()
    if events.is_file():
        for line in events.read_text().splitlines():
            event=json.loads(line)
            if event.get('phase')=='case-start':started.add(event['id'])
            elif event.get('phase')=='case-terminal':found[event['id']]=event
    if (set(found)|started)-set(ids):raise ValueError('worker event ID escaped selected bucket')
    cases=[]
    for identity in ids:
        if identity in found:
            row={k:v for k,v in found[identity].items() if k not in ('phase','at_utc')}
        elif identity in started:
            row={'id':identity,'result':'INTERRUPTED-ACTIVE-METHOD','executed':False}
        else:
            row={'id':identity,'result':'NOT-RUN-BOUNDED-STOP' if events.is_file() else 'NOT-RUN-UNSAFE-PARALLEL-QUEUE','executed':False}
        cases.append(row)
    rows.append({'bucket':bucket,'cases':cases,'events_sha256':sha(events) if events.is_file() else None,
                 'log_sha256':sha(log) if log.is_file() else None})
cases=[case for row in rows for case in row['cases']]
ids=[identity for methods in buckets.values() for identity in methods]
if len(ids)!=345 or [case['id'] for case in cases]!=ids:raise ValueError('exact 345 case accounting differs')
result={'schema_version':'lab-T16-API61-unsafe-parallel-sample/v1-candidate',
        'run_id':'api61-full-20261023','selected_source_sha256':selection['api_source_sha256'],
        'selected_profile_sha256':selection['api_profile_sha256'],
        'selection_sha256':sha(RUN/'SELECTION.json'),'inventory_sha256':sha(INVENTORY),
        'selected_method_count':345,'terminal_accounting_count':len(cases),
        'actually_terminal_method_count':len([c for c in cases if c['result'] not in ('INTERRUPTED-ACTIVE-METHOD','NOT-RUN-BOUNDED-STOP','NOT-RUN-UNSAFE-PARALLEL-QUEUE')]),
        'actual_pass_count':sum(c['result']=='PASS' for c in cases),
        'actual_fail_count':sum(c['result']=='FAIL' for c in cases),
        'bucket_results':rows,'result':'INCOMPLETE-UNSAFE-PARALLEL-SAMPLE',
        'stop_reason':'One inherited class mutates selected shared API files in tamper tests, so concurrent source guards are unsafe; stopped before those tests.',
        'selected_api_files_unchanged_after_stop':True,
        't16_qualified':False,'authority_effect':'none',
        'recorded_at_utc':datetime.now(timezone.utc).isoformat()}
target=RUN/'INTERRUPTED-LEDGER.json'
with target.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps({'receipt':str(target),'sha256':sha(target),
                  'accounted':len(cases),'actually_terminal':result['actually_terminal_method_count'],
                  'actual_fail':result['actual_fail_count']},sort_keys=True))

#!/usr/bin/env python3
"""Record the observed Q fit-enum failure and dependent D skip; never retry."""
import argparse, datetime, hashlib, json
from pathlib import Path
R = Path(__file__).resolve().parents[1]

def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def record(uid):
    unit = next(u for u in read(R / 'schedule.json')['units'] if u['unit_id'] == uid)
    assert unit['phase'] == 'bundle' and unit['roles'] == ['Z', 'A', 'Q', 'D']
    rc_path = R / 'receipts' / f'{uid}-Q.json'
    rc = read(rc_path)
    validation = rc['artifact_validation']
    assert rc['join_status'] == 'completed' and validation['valid'] is False
    assert validation['errors'] and set(validation['errors']) == {'fit enum'}, 'Another error requires explicit disposition'
    output = R / validation['output']
    assert sha(output) == validation['sha256']
    for role in ['Z', 'A']:
        assert read(R / 'receipts' / f'{uid}-{role}.json')['artifact_validation']['valid']
    events_path = R / 'receipts/events.jsonl'
    events = [json.loads(line) for line in events_path.read_text().splitlines()]
    joins = [e for e in events if e['unit_id'] == uid and e['role'] == 'Q' and e['event'] == 'join']
    assert len(joins) == 1 and joins[0]['agent_id'] == rc['agent_id']
    assert not any(e['unit_id'] == uid and e['role'] == 'D' and e['event'] in ['spawn', 'join'] for e in events)
    assert not (R / 'outputs' / uid / 'D.json').exists()
    disposition_path = R / 'receipts' / f'{uid}-D-disposition.json'
    assert not disposition_path.exists(), 'Disposition already saved; inspect instead of duplicating'
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    disposition = {'observed_at_utc': now, 'event': 'skip_dependency', 'unit_id': uid,
                   'role': 'D', 'agent_id': None, 'native_invocation': False,
                   'reason': 'Required Q dependency terminal-joined with invalid fit enum under frozen validator; zero retries and no substantive hand repair.',
                   'dependency_receipt': str(rc_path.relative_to(R)),
                   'dependency_receipt_sha256': sha(rc_path),
                   'dependency_output_sha256': sha(output),
                   'disposition': 'not_executed_dependency_failed'}
    ledger = R / 'reports/execution-failures.jsonl'
    prior = [json.loads(line) for line in ledger.read_text().splitlines()] if ledger.exists() else []
    assert not any(e['unit_id'] == uid for e in prior)
    failure = {'unit_id': uid, 'phase': 'bundle', 'case_id': unit['case_id'],
               'condition': unit['condition'], 'status': 'execution_failed',
               'observed_at_utc': now, 'failed_role': 'Q',
               'failure_kind': 'output_contract_validation', 'errors': validation['errors'],
               'output_preserved': str(output.relative_to(R)), 'output_sha256': sha(output),
               'skipped_roles': [{'role': 'D', 'receipt': str(disposition_path.relative_to(R))}],
               'retries': 0, 'raw_substantive_repair': False,
               'comparison_disposition': 'Execution-quality outcome; not zero novelty or completed full scaffold.',
               'contract_note': 'Frozen critique prompt does not enumerate fit values; validator requires a fixed enum. Same interface omission recorded in B001.'}
    disposition_path.write_text(json.dumps(disposition, indent=2) + '\n')
    with events_path.open('a') as stream: stream.write(json.dumps(disposition) + '\n')
    with ledger.open('a') as stream: stream.write(json.dumps(failure) + '\n')
    return failure

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('unit')
    args = parser.parse_args()
    print(json.dumps(record(args.unit), indent=2))

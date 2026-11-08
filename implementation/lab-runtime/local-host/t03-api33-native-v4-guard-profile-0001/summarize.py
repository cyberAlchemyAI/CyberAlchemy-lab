"""Cold, bounded accounting of the one live Lesson selection profile."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_API = 'd2cc82418a643118d27bd5c539a0aca794cde1018856c0ac99bf381b3e875eb7'
EXPECTED_PROFILE = 'e509e783065ce9650756b8a40a1bb6c0dcc31d84393b16c137bba95ff46f47d5'
EXPECTED_DRIVER = 'e8d12bac33750a4b3d0dee0d1a665e07602c87399d173e17f162bf680911af54'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(rows, stage):
    found = [row for row in rows if row.get('stage') == stage]
    if len(found) != 1:
        raise ValueError('profile stage count differs: ' + stage)
    return found[0]


def summarize():
    if sha(HERE / 'run_selection.py') != EXPECTED_DRIVER:
        raise ValueError('driver changed')
    receipt = json.loads((HERE / 'RESULT.json').read_bytes())
    lines = [json.loads(line) for line in (HERE / 'progress.jsonl').read_text().splitlines()]
    if receipt['api_manifest_sha256'] != EXPECTED_API or receipt['profile_sha256'] != EXPECTED_PROFILE:
        raise ValueError('selected API/profile differs')
    if (receipt['lesson_selected'], receipt['lesson_applied'], receipt['lesson_assessed']) != (True, False, False):
        raise ValueError('Lesson result overclaimed')
    if receipt['owned_private_fixture_removed'] is not True:
        raise ValueError('private fixture cleanup not observed')
    if sum(item['posture'] == 'selected' for item in receipt['lesson_result']['items']) != 1:
        raise ValueError('selected count differs')
    opened = one(lines, 'session-open-result')
    entered = one(lines, 'lesson-select-entry')
    selected = one(lines, 'lesson-select-result')
    if not (opened['monotonic_ns'] < entered['monotonic_ns'] < selected['monotonic_ns'] < receipt['ending']['monotonic_ns']):
        raise ValueError('observed monotonic order differs')
    if selected['reply_sha256'] != receipt['lesson_reply_sha256']:
        raise ValueError('selected reply digest differs')
    expiry = datetime.fromisoformat(receipt['session_expires_at'].replace('Z', '+00:00'))
    close_time = datetime.fromisoformat(receipt['ending']['utc'])
    if not (expiry.tzinfo is not None and close_time.tzinfo is not None and close_time < expiry):
        raise ValueError('Session close was not before expiry')
    guards = [line for line in lines if line.get('kind') == 'T03-guard-profile']
    by_stage = defaultdict(list)
    for line in guards:
        if type(line['elapsed_ns']) is not int or line['elapsed_ns'] < 0:
            raise ValueError('invalid measured duration')
        by_stage[line['stage']].append(line['elapsed_ns'])
    expected = {'init-host-source-guard':1, 'host-source-guard':5,
        'machine-peer-guard':5, 'schema-guard':5, 'vault-guard':5,
        'resource-guard':5, 'session-selected':5, 'parent-policy-guard':5,
        'host-guard-total':5}
    if {stage:len(values) for stage,values in by_stage.items()} != expected:
        raise ValueError('profile stages incomplete')
    for ordinal in range(1, 6):
        rows = [line for line in guards if line['ordinal'] == ordinal]
        if len(rows) != 8 or rows[-1]['stage'] != 'host-guard-total':
            raise ValueError('ordinal profile incomplete')
        if any(a['ended_monotonic_ns'] >= b['ended_monotonic_ns'] for a,b in zip(rows,rows[1:])):
            raise ValueError('ordinal profile ordering differs')
    elapsed_ns = selected['monotonic_ns'] - entered['monotonic_ns']
    guard_ns = sum(by_stage['host-guard-total'])
    measured_sub_ns = sum(sum(values) for stage,values in by_stage.items()
                          if stage not in ('init-host-source-guard','host-guard-total'))
    return {'schema_version':'lab-T03-d95-selection-guard-profile/v1-candidate',
        'api_manifest_sha256':EXPECTED_API, 'profile_sha256':EXPECTED_PROFILE,
        'driver_sha256':EXPECTED_DRIVER,
        'live_receipt_sha256':sha(HERE/'RESULT.json'),
        'progress_sha256':sha(HERE/'progress.jsonl'),
        'session_open_utc':opened['utc'], 'session_expires_at':receipt['session_expires_at'],
        'session_close_utc':receipt['ending']['utc'],
        'selection_elapsed_ns':elapsed_ns, 'host_guard_total_ns':guard_ns,
        'host_guard_fraction_of_selection':round(guard_ns/elapsed_ns,6),
        'guard_stage_elapsed_ns':{stage:values for stage,values in sorted(by_stage.items())},
        'guard_unattributed_ns':guard_ns-measured_sub_ns,
        'lesson_selected':True,'lesson_applied':False,'lesson_assessed':False,
        'owned_private_fixture_removed':True,'authority_effect':'none',
        'claim_ceiling':'Selection-only timing and Session close; no application, assessment or optimization outcome.'}


if __name__ == '__main__':
    print(json.dumps(summarize(),sort_keys=True,indent=2))

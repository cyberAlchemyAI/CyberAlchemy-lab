#!/usr/bin/env python3
"""Add terminal failure accounting without changing the frozen integrity audit.

This checks persisted artifacts and recorded native events, not idea quality.
"""
import collections
import datetime
import hashlib
import json
from pathlib import Path
from audit_integrity import audit

R = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((R / path).read_text())

def sha(path):
    return hashlib.sha256((R / path).read_bytes()).hexdigest()

def run():
    original = audit()
    errors = list(original['errors'])
    pending = list(original['pending'])
    checks = 0
    def check(ok, message):
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(message)
    def bound(path, digest, label):
        check((R / path).is_file() and sha(path) == digest, label)
    events = [json.loads(x) for x in (R / 'receipts/events.jsonl').read_text().splitlines()]
    index = collections.defaultdict(list)
    for event in events:
        index[(event['unit_id'], event['role'])].append(event)
    schedule = read('schedule.json')
    scored = schedule['units'] + read('confirmation-schedule.json')['units']
    units = [dict(schedule['preflight'], phase='preflight')] + scored
    scheduled = {u['unit_id']: u for u in units}
    check(len(scored) == 120 and len(scheduled) == 121, 'Frozen schedule coverage differs')
    failures = [json.loads(x) for x in (R / 'reports/execution-failures.jsonl').read_text().splitlines()]
    failed = {f['unit_id']: f for f in failures}
    check(len(failed) == len(failures), 'Duplicate execution failure disposition')
    for uid, failure in failed.items():
        before = len(errors)
        check(uid in scheduled and scheduled[uid]['phase'] == 'bundle', uid + ': unexpected failure scope')
        check(failure['failed_role'] == 'Q' and failure['retries'] == 0 and failure['raw_substantive_repair'] is False, uid + ': failure policy differs')
        receipt = read(f'receipts/{uid}-Q.json')
        value = receipt['artifact_validation']
        check(receipt['join_status'] == 'completed' and value['valid'] is False, uid + ': invalid failure receipt')
        bound(failure['output_preserved'], failure['output_sha256'], uid + ': failed raw bytes changed')
        check(value['sha256'] == failure['output_sha256'], uid + ': failure hash mismatch')
        manifest = read(f'prompts/jobs/{uid}-Q.manifest.json')
        bound(f'prompts/jobs/{uid}-Q.txt', manifest['prompt_sha256'], uid + ': failed prompt changed')
        bound(f'cases/{scheduled[uid]["case_id"]}.json', manifest['case_sha256'], uid + ': failed case changed')
        check(manifest['case_id'] == scheduled[uid]['case_id'] and manifest['unit_id'] == uid and manifest['role'] == 'Q', uid + ': failed role binding differs')
        check(Path(manifest['expected_output']) == R / failure['output_preserved'], uid + ': failed output path differs')
        role_events = index[(uid, 'Q')]
        spawns = [e for e in role_events if e['event'] == 'spawn']
        joins = [e for e in role_events if e['event'] == 'join']
        check(len(spawns) == len(joins) == 1, uid + ': failed native receipt coverage')
        check([Path(s['path']).stem for s in manifest['source_outputs']] == ['Z', 'A'], uid + ': failed Q source roles differ')
        for source in manifest['source_outputs']:
            path = Path(source['path'])
            bound(path, source['sha256'], uid + ': failed Q source changed')
            check(path.parent == R / 'outputs' / uid, uid + ': failed Q source from another unit')
            prior = [e for e in index[(uid, path.stem)] if e['event'] == 'join']
            check(len(prior) == 1 and len(spawns) == 1 and prior[0]['artifact_validation']['valid'] and prior[0]['observed_at_utc'] <= spawns[0]['observed_at_utc'], uid + ': failed Q prerequisite/order differs')
        skip = read(f'receipts/{uid}-D-disposition.json')
        check(skip['event'] == 'skip_dependency' and skip['native_invocation'] is False and skip['disposition'] == 'not_executed_dependency_failed', uid + ': dependent skip differs')
        bound(skip['dependency_receipt'], skip['dependency_receipt_sha256'], uid + ': failed dependency receipt changed')
        check(skip['dependency_output_sha256'] == value['sha256'], uid + ': skip output binding differs')
        check(not (R / 'outputs' / uid / 'D.json').exists(), uid + ': skipped D output exists')
        check(index[(uid, 'D')] == [skip], uid + ': skipped D has unexpected native events')
        if len(errors) == before:
            for item in [f'{uid}/Q: execution quality failure', f'{uid}/D: no terminal receipt']:
                check(item in pending, uid + ': original failure classification missing')
                if item in pending:
                    pending.remove(item)
    bindings = 0
    for manifest_path in sorted(R.glob('*manifest.json')):
        manifest = read(manifest_path)
        for row in manifest.get('files', []):
            path = row.get('path', row.get('prompt'))
            if path is None or 'sha256' not in row:
                continue
            bound(path, row['sha256'], str(manifest_path.name) + ': binding changed: ' + path)
            bindings += 1
            if 'manifest_sha256' in row:
                bound(str(Path(path).with_suffix('.manifest.json')), row['manifest_sha256'], 'Confirmation prompt manifest changed: ' + path)
    freeze = read('finalist-freeze.json')
    for row in freeze['source_bindings']:
        bound(row['path'], row['sha256'], 'Finalist source changed: ' + row['path'])
    first_confirmation = min(e['observed_at_utc'] for e in events if e['event'] == 'spawn' and e['unit_id'].startswith('H'))
    check(freeze['frozen_at_utc'] < read('confirmation-prompts-manifest.json')['prepared_at_utc'] < first_confirmation, 'Confirmation preceded finalist/prompt freeze')
    rows = []
    for unit in units:
        uid = unit['unit_id']
        joins = [e for role in unit['roles'] for e in index[(uid, role)] if e['event'] == 'join']
        complete = len(joins) == len(unit['roles']) and all(e['artifact_validation']['valid'] for e in joins)
        rows.append({'unit_id': uid, 'phase': unit['phase'], 'state': 'execution_failed' if uid in failed else ('completed_valid' if complete else 'pending'), 'native_roles_joined': len(joins)})
    return {'status': 'fail' if errors else ('in_progress' if pending else 'pass_for_generation_dispositions'), 'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks': checks, 'manifest_bindings': bindings, 'original_integrity_counts': original['counts'], 'terminal_failed_units': sorted(failed), 'states': dict(collections.Counter(x['state'] for x in rows if x['phase'] != 'preflight')), 'pending_count': len(pending), 'pending': pending, 'errors': errors, 'units': rows, 'limits': ['Complements the original integrity audit; it does not erase its preserved pending classifications for failed roles.', 'Native terminal events are orchestrator-observed receipts, not platform attestation.', 'No assessment completeness, novelty, equal compute or world benefit verdict.']}

if __name__ == '__main__':
    result = run()
    (R / 'reports/disposition-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['units', 'pending']}, indent=2))
    raise SystemExit(bool(result['errors']))

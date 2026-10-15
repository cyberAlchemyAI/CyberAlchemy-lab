#!/usr/bin/env python3
"""Account for completed native attempts and saved text, without compute inference."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((R / path).read_text())

def sha(path):
    return hashlib.sha256((R / path).read_bytes()).hexdigest()

def events(path):
    return [json.loads(line) for line in (R / path).read_text().splitlines()]

def main():
    schedule = read('schedule.json')
    units = [dict(schedule['preflight'], phase='preflight')] + schedule['units'] + read('confirmation-schedule.json')['units']
    generation = events('receipts/events.jsonl')
    spawns = [e for e in generation if e['event'] == 'spawn']
    joins = [e for e in generation if e['event'] == 'join']
    skips = [e for e in generation if e['event'] == 'skip_dependency']
    key = lambda e: (e['unit_id'], e['role'])
    assert len(spawns) == len({key(e) for e in spawns}) == len({e['agent_id'] for e in spawns})
    assert len(joins) == len({key(e) for e in joins})
    assert {key(e) for e in spawns} == {key(e) for e in joins}
    joined = {key(e): e for e in joins}
    skipped = {key(e): e for e in skips}
    assert len(skipped) == len(skips) and not set(skipped) & set(joined)
    expected = {(u['unit_id'], role) for u in units for role in u['roles']}
    assert set(joined) | set(skipped) == expected
    recovered = []
    missing = []
    rows = []
    by_phase = collections.defaultdict(collections.Counter)
    valid_roles = 0
    terminal_messages = 0
    for u in units:
        uid = u['unit_id']
        roles = []
        for role in u['roles']:
            k = (uid, role)
            if k in skipped:
                roles.append({'role': role, 'status': 'skipped_dependency', 'saved_words': None})
                continue
            receipt = read(f'receipts/{uid}-{role}.json')
            v = receipt['artifact_validation']
            assert receipt['agent_id'] == joined[k]['agent_id']
            valid_roles += v['valid']
            if receipt.get('native_handle_missing_observed'):
                assert receipt['native_terminal_response_observed'] is False
                assert sha(receipt['native_observation_witness']) == receipt['native_observation_witness_sha256']
                recovered.append({'unit_id': uid, 'role': role, 'receipt': f'receipts/{uid}-{role}.json'})
            else:
                assert receipt['close_reason'].startswith('Terminal native response observed')
                terminal_messages += 1
            p = R / 'outputs' / uid / f'{role}.json'
            if p.exists():
                assert sha(str(p.relative_to(R))) == v['sha256']
                words = len(p.read_text().split())
                assert words == v['words']
            else:
                assert not v['valid'] and 'missing output' in v['errors']
                missing.append({'unit_id': uid, 'role': role})
                words = None
            roles.append({'role': role, 'status': 'valid' if v['valid'] else 'failed', 'saved_words': words})
        complete = all(r['status'] == 'valid' for r in roles)
        saved = [r['saved_words'] for r in roles if r['saved_words'] is not None]
        row = {'unit_id': uid, 'phase': u['phase'], 'condition': u['condition'], 'complete_valid': complete, 'roles': roles, 'known_saved_output_words': sum(saved), 'complete_workflow_output_words': sum(saved) if complete else None}
        rows.append(row)
        phase = by_phase[u['phase']]
        phase.update(attempts=1, complete_valid=int(complete), failed=int(not complete), invoked_roles=sum(r['status'] != 'skipped_dependency' for r in roles), skipped_roles=sum(r['status'] == 'skipped_dependency' for r in roles), known_saved_output_words=sum(saved))
    reviews = events('receipts/review-events.jsonl')
    review_spawns = [e for e in reviews if e['event'] == 'spawn']
    review_joins = [e for e in reviews if e['event'] == 'join']
    assert len(review_spawns) == len({e['agent_id'] for e in review_spawns})
    assert len(review_joins) == len(review_spawns)
    assert {e['agent_id'] for e in review_spawns} == {e['agent_id'] for e in review_joins}
    review_words = 0
    for e in review_joins:
        p = Path(e['output'])
        assert hashlib.sha256(p.read_bytes()).hexdigest() == e['output_sha256']
        review_words += len(p.read_text().split())
    independent = [e for e in review_spawns if e.get('judge_id') in ['J1', 'J2']]
    adjudicators = [e for e in review_spawns if e.get('role') == 'adjudicator']
    assert len(independent) == 16 and len(adjudicators) == 8
    pair_assessments = sum(e['pair_assessments'] for e in independent)
    assert pair_assessments == 240
    sources = ['schedule.json', 'confirmation-schedule.json', 'receipts/events.jsonl', 'receipts/review-events.jsonl', 'reports/execution-failures.jsonl', 'native-handle-recovery-evidence-manifest.json']
    result = {'status': 'complete_attempt_accounting', 'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'scored_units': len(units)-1, 'valid_scored_workflows': sum(r['complete_valid'] for r in rows if r['phase'] != 'preflight'), 'failed_scored_attempts': sum(not r['complete_valid'] for r in rows if r['phase'] != 'preflight'), 'separate_preflight_units': 1, 'nominal_generation_roles': len(expected), 'actual_generation_role_invocations': len(spawns), 'dependent_skips': len(skips), 'valid_role_outputs_including_preflight': valid_roles, 'failed_roles': len(joins)-valid_roles, 'saved_generation_artifacts': sum(r['saved_words'] is not None for u in rows for r in u['roles']), 'missing_outputs': missing, 'observed_native_terminal_responses': terminal_messages, 'recovered_absent_handle_joins': recovered, 'known_saved_generation_output_words': sum(r['known_saved_output_words'] for r in rows), 'all_generation_output_words': None if missing else sum(r['known_saved_output_words'] for r in rows), 'independent_review_agents': len(independent), 'independent_pair_assessments': pair_assessments, 'bounded_adjudicator_agents': len(adjudicators), 'saved_review_and_adjudication_words': review_words, 'by_phase': dict(by_phase), 'units': rows, 'sources': [{'path': p, 'sha256': sha(p)} for p in sources], 'tool_sha256': sha('tools/report_execution_accounting.py'), 'limits': ['Counts cover generation and scored semantic review; case/archive authoring, preflight auditing, orchestration and final completion auditing are additional work outside these role counts.', 'Native events are parent-recorded observations, not platform attestation. Two joins recover valid saved outputs after verified native handle absence; they do not claim an observed terminal response.', 'Saved word counts include JSON representation. Missing output has unknown size; no complete run cost can be inferred from known persisted text.', 'Actual tokens, internal model calls, model seeds and hidden compute are unavailable. Soft allocations do not establish equal compute.', 'Observed spawn/join timestamps are orchestration observations, not precise model runtimes.', 'A valid JSON artifact or a completed assessment establishes neither empirical effectiveness nor worldwide originality.']}
    out = R / 'reports/execution-accounting.json'
    assert not out.exists(), 'Final accounting already saved'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['units', 'sources', 'limits']}, indent=2))

if __name__ == '__main__':
    main()

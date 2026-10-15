#!/usr/bin/env python3
"""Verify persisted execution coverage and evidence integrity; no model efficacy claim."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((ROOT / path).read_text())

def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def resolve(ref):
    path, _, pointer = ref.partition('#')
    assert (ROOT / path).is_file(), ref
    if pointer:
        value = read(path)
        assert pointer.startswith('/'), ref
        for part in pointer[1:].split('/'):
            part = part.replace('~1', '/').replace('~0', '~')
            value = value[int(part)] if isinstance(value, list) else value[part]


def verify():
    manifest = read('inputs/manifest.json')
    assert len(manifest) == 22
    for entry in manifest:
        assert sha(entry['snapshot']) == entry['sha256'], entry['snapshot']
    catalog = read('inputs/catalog.json')
    ids = [row['id'] for row in catalog['strategies']]
    assert ids == [f'S{i:02d}' for i in range(1, 17)]
    matrix = read('completion-matrix.json')
    assert matrix['task_status'] == 'completed'
    assert all(s['task_status'] == 'completed' and all(t['status'] == 'completed' for t in s['required_steps']) for s in matrix['strategies'])
    events = [json.loads(line) for line in (ROOT / 'observability.jsonl').read_text().splitlines()]
    outputs = evidence_count = executed = exits = 0
    for sid in ids:
        source = read(f'inputs/dispatches/{sid.lower()}.dispatch.json')
        result = read(f'strategies/{sid}.json')
        assert result['task_status'] == 'completed'
        assert result['independent_review_status'] == 'pass'
        assert [(g['gate_id'], g['condition']) for g in source['gates']] == [(g['gate_id'], g['condition']) for g in result['gates']]
        assert len(source['steps']) == len(result['steps'])
        for step, actual in zip(source['steps'], result['steps']):
            assert step['step_id'] == actual['step_id']
            assert step['capability_ref'] == actual['capability_ref']
            output = actual['output']
            assert output in [x['ref'] for x in step['outputs']]
            data = read(output)
            assert data['strategy_id'] == sid and data['step_id'] == step['step_id']
            assert data['input_refs'] == step['inputs']
            assert sha(output) == actual['sha256']
            receipt = read(actual['execution_receipt'])
            assert receipt['output_sha256'] == actual['sha256']
            assert receipt['runtime_admission_claim'] is False
            if sid == 'S14':
                assert receipt['receipt_kind'] == 'declared-direct-exit-evidence'
                exits += 1
            else:
                assert receipt['receipt_kind'] == 'executed-step-evidence'
                executed += 1
            for ref in data['evidence']:
                resolve(ref)
            if actual['evidence_artifact']:
                resolve(actual['evidence_artifact'])
                evidence_count += 1
            outputs += 1
        source_events = set(source['observability']['trace_events'])
        observed = {e['event'] for e in events if e['strategy_id'] == sid}
        if sid == 'S14':
            source_events.remove('step_output_observed')
            source_events.add('direct_exit_evaluated')
        assert source_events <= observed, (sid, source_events - observed)
    for event in events:
        assert 'retrospective' in event['recording_mode']
        for ref in event['evidence']:
            resolve(ref)
    assert (outputs, executed, exits, evidence_count) == (47, 45, 2, 7)
    assert len(read('execution-receipts.json')['receipts']) == outputs
    primary = read('experiments/results.json')
    assert len(primary['arms']) == 3
    for arm in primary['arms']:
        assert arm['errors'] == [] and len(arm['evaluated']) == 12
        assert all(row['feasible'] and row['best_under_stipulated_model'] for row in arm['evaluated'])
        assert sha('experiments/' + arm['output']) == arm['output_sha256']
    factorial = read('experiments/factorial/results.json')
    assert len(factorial['cells']) == 4
    for cell in factorial['cells']:
        assert cell['errors'] == [] and cell['appropriate'] == 4
        assert sha(f"experiments/factorial/outputs/{cell['arm']}.json") == cell['output_sha256']
    ledger = read('agent-ledger.json')
    agents = ledger['records'] + ledger['experiment_agents'] + ledger['review_agents']
    assert len(agents) == 12 and all(a['join_status'] == 'completed' for a in agents)
    review = read('audit/completion-review.json')
    assert review['acceptance_verdict'] == 'pass' and review['user_goal_ready'] is True
    assert all(s['acceptance_verdict'] == 'pass' for s in review['strategies'])
    assert read('audit/experiment-review.json')['acceptance'] == 'pass'
    shape = read('audit/frozen-dispatch-validation.json')
    assert len(shape['results']) == 16 and all(r['validation'] == 'pass' for r in shape['results'])
    return dict(status='pass', scope='Coverage, evidence integrity, source trace mapping, and independent acceptance; no production efficacy inference.', strategies=16, required_output_records=outputs, executed_stages=executed, declared_direct_exit_records=exits, required_evidence_artifacts=evidence_count, frozen_hashes=len(manifest), joined_helpers=len(agents), retrospective_events=len(events), native_fixed_choice_decisions=52)

if __name__ == '__main__':
    result = verify()
    (ROOT / 'audit/execution-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

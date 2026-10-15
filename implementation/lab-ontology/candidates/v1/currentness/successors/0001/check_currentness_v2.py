#!/usr/bin/env python3
"""Check current active proof bindings against the preserved preparation baseline."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import portable
ROOT = portable.ROOT
HERE = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PLAN = HERE.parents[1]
CLOSED = {'complete', 'complete-existing-evidence', 'complete-planning', 'satisfied-scoped'}


def load(path):
    return json.loads(path.read_text())


def changed(rows):
    bad = []
    for row in rows:
        path = ROOT / row['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            bad.append(row['path'])
    return sorted(set(bad))


def main():
    portable_errors, portable_observations = portable.currentness()
    baseline = load(HERE / 'preparation-baseline.json')
    sources = load(PLAN / 'SOURCE-BASELINE.json')['sources']
    dag = load(HERE / 'dag.json'); nodes = {n['id']: n for n in dag['nodes']}
    manifest = load(HERE / 'swu-manifest.json')
    active, swu_bad = [], []
    for node in dag['nodes']:
        refs = node.get('completion_evidence', node.get('progress_evidence', []))
        for binding in refs:
            mismatches = changed([binding])
            receipt = load(ROOT / binding['path'])
            mismatches += changed(receipt.get('files', receipt.get('source_files', [])) + receipt.get('source_bindings', []))
            if receipt.get('result') != 'PASS': mismatches.append('non-passing-receipt')
            if node['status'] in CLOSED and receipt.get('task_complete') is False:
                mismatches.append('partial-proof-cannot-close-task')
            active.append({'task': node['id'], 'receipt': binding['path'],
                           'result': 'FLAG' if mismatches else 'PASS', 'changed': sorted(set(mismatches))})
        if node['status'] in CLOSED | {'in-progress'} and not refs:
            active.append({'task': node['id'], 'receipt': None, 'result': 'FLAG', 'changed': ['missing-active-evidence']})
    for unit in manifest['units']:
        parent = nodes[unit['parent_task']]
        if parent['status'] in CLOSED | {'in-progress'}:
            if unit.get('status') != parent['status']:
                swu_bad.append(unit['id'] + ':status')
            for key in ['completion_evidence', 'progress_evidence']:
                if key in parent and unit.get(key) != parent[key]: swu_bad.append(unit['id'] + ':' + key)
    old_bad = changed(baseline['files']); source_bad = changed(sources)
    result = {'schema_version': 'lab-construction-currentness/v2-candidate', 'authority_effect': 'none',
        'result': 'PASS' if not portable_errors and not old_bad and not source_bad and not swu_bad and all(x['result'] == 'PASS' for x in active) else 'FLAG',
        'checked_at': datetime.now(timezone.utc).isoformat(), 'active_receipt_checks': active,
        'original_preparation_files': len(baseline['files']), 'original_bound_sources': len(sources),
        'portable_locator_mismatches': portable_errors, 'portable_locator_observations': portable_observations,
        'original_preparation_mismatches': old_bad, 'source_mismatches': source_bad, 'swu_mismatches': swu_bad,
        'completed_tasks': sum(n['status'] in CLOSED for n in dag['nodes']), 'total_tasks': len(dag['nodes']),
        'in_progress_tasks': [n['id'] for n in dag['nodes'] if n['status'] == 'in-progress'],
        'owner_checkpoint_outcome': None, 'real_operational_stores_provisioned': 0, 'repository_admissions_applied': 0,
        'goal_complete': False,
        'claim_ceiling': 'Current linked candidate evidence and exact preserved preparation baseline only; no complete plan, canonical admission, human pilot, stable release or live operations.'}
    receipts = HERE / 'currentness-receipts'; receipts.mkdir(exist_ok=True)
    index = 1
    while (receipts / f'{index:04d}.json').exists(): index += 1
    result['checker_binding'] = {'path': Path(__file__).resolve().relative_to(ROOT).as_posix(),
                                 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    raw = json.dumps(result, indent=2, sort_keys=True) + '\n'
    (receipts / f'{index:04d}.json').write_text(raw)
    (HERE / 'evidence-currentness.json').write_text(raw)
    print(json.dumps({'result': result['result'], 'closed': result['completed_tasks'], 'total': result['total_tasks'],
                      'active_receipts': len(active), 'original_files': len(baseline['files']), 'sources': len(sources),
                      'changes': portable_errors + old_bad + source_bad + swu_bad + [x for r in active for x in r['changed']]}))
    raise SystemExit(0 if result['result'] == 'PASS' else 1)


if __name__ == '__main__': main()

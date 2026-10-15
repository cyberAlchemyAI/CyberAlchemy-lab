#!/usr/bin/env python3
"""Native attempt/source/word accounting; no semantic success inferred."""
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parents[1]
DISPATCH = 'process-novelty-allten-2026-10-08'


def summarize(jobs, states, events):
    joins = {e['job_id']: e for e in events if e.get('event') == 'join'}
    spawns = {e['job_id']: e for e in events if e.get('event') == 'spawn'}
    preparations = {e['job_id']: e for e in events if e.get('event') == 'prepare'}
    result = []
    for job in jobs:
        identifier = job['job_id']
        joined, prepared = joins.get(identifier, {}), preparations.get(identifier, {})
        result.append({'job_id': identifier, 'case_id': job['case_id'],
                       'stage': job['stage'], 'role': job['role'],
                       'status': states[identifier]['status'],
                       'agent_id': spawns.get(identifier, {}).get('agent'),
                       'native_spawned': identifier in spawns,
                       'native_terminal_observed': joined.get('terminal_observed'),
                       'output_sha256': joined.get('sha256'),
                       'known_saved_words': joined.get('known_words'),
                       'input_word_proxy': (sum(x['word_proxy'] for x in prepared['sources'])
                                            + prepared['prompt']['word_proxy']) if prepared else None})
    return {'dispatch_id': DISPATCH, 'attempts': len(result),
            'states': dict(Counter(row['status'] for row in result)),
            'native_spawns': sum(row['native_spawned'] for row in result),
            'native_terminal_joins': sum(row['native_terminal_observed'] is True for row in result),
            'known_saved_words': sum(row['known_saved_words'] for row in result
                                    if row['known_saved_words'] is not None),
            'rows': result,
            'limits': 'Saved words/input proxies exclude internal calls/tokens. Shared sources recur in workflow context; skipped roles are not successful outputs.'}


def build(root=R):
    root = Path(root)
    spec = importlib.util.spec_from_file_location('accounting_runtime', root / 'tools/runtime.py')
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    jobs = list(runtime.schedule()[0].values())
    states, events = runtime.status()['jobs'], runtime.events()
    scored = [j for j in jobs if j['stage'] != 'preflight']
    report = summarize(scored, states, events)
    report['scheduled_preflight'] = summarize([j for j in jobs if j['stage'] == 'preflight'], states, events)
    report['external_native_receipts'] = [e for e in events if e.get('event') in {
        'review_spawn', 'review_join', 'adjudication_spawn', 'adjudication_join', 'audit_spawn', 'audit_join',
        'prep_preflight_extension_spawn', 'prep_preflight_extension_join',
        'prep_review_preflight_spawn', 'prep_review_preflight_join'}]
    groups = {
        'main-raw-terminals': [j for j in scored if j['stage'] == 'main' and j['role'] in ['Z', 'A']],
        'critique-terminals': [j for j in scored if j['stage'] == 'critique' and j['role'] == 'Q'],
        'neutral-D-terminals': [j for j in scored if j['stage'] in ['main', 'critique'] and j['role'] == 'D'],
        'p08-terminals': [j for j in scored if j['stage'] == 'p08'],
        'p09-terminals': [j for j in scored if j['stage'] == 'p09']}
    for name, selected in groups.items():
        evidence = summarize(selected, states, events)
        evidence['all_terminal_dispositions'] = all(states[j['job_id']]['status'] in ['valid', 'failed', 'skipped'] for j in selected)
        (root / 'receipts' / (name + '.json')).write_text(json.dumps(evidence, indent=2) + '\n')
    (root / 'reports/execution-accounting.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    report = build()
    print(json.dumps({k: v for k, v in report.items() if k not in ['rows', 'external_native_receipts', 'scheduled_preflight']}, indent=2))

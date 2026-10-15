#!/usr/bin/env python3
"""Keep every planned unit visible when independent review coverage fails.

No assessment is invented: scalar values are null and candidate bytes remain
bound to their original sources. The failed resolved report is preserved.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def rows(root, relative):
    path = root / relative
    if not path.exists():
        return [], {'path': relative, 'sha256': None, 'unreadable': 'missing'}
    data = path.read_bytes()
    binding = {'path': relative, 'sha256': hashlib.sha256(data).hexdigest()}
    try:
        document = json.loads(data)
        items = document.get('openings', [])
        if not isinstance(items, list):
            raise ValueError('openings not list')
        return [x for x in items if isinstance(x, dict) and isinstance(x.get('id'), str)], binding
    except (ValueError, AttributeError) as error:
        binding['unreadable'] = str(error)
        return [], binding


def gate_main(root, case, schedule, states, failed):
    units, bindings = [], []
    for unit in schedule['units']:
        if unit['case_id'] != case:
            continue
        raw = []
        for job in unit['raw_jobs']:
            candidates, binding = rows(root, 'outputs/' + job + '.json')
            bindings.append(binding)
            for candidate in candidates:
                raw.append({'raw_id': candidate['id'], 'family_id': None,
                            'kind': None, 'novelty': None, 'usefulness': None, 'fit': None,
                            'observability': None, 'support': None, 'retention': None,
                            'contract': None, 'intelligible': None,
                            'judgment_resolved': False, 'raw_judgment_resolved': False,
                            'assessment_disposition': 'unassessed_review_failure',
                            'claim': candidate.get('claim'), 'source_opening': candidate,
                            'source_sha256': binding['sha256']})
        _, post_binding = rows(root, 'outputs/' + unit['post_job'] + '.json')
        bindings.append(post_binding)
        all_jobs = unit['raw_jobs'] + [unit['post_job']]
        valid = all(states[j]['status'] == 'valid' for j in all_jobs)
        observed_words = sum(len((root / ('outputs/' + j + '.json')).read_text().split())
                             for j in all_jobs if (root / ('outputs/' + j + '.json')).exists())
        units.append({'unit_id': unit['unit_id'], 'condition': unit['condition'],
                      'repetition': unit['repetition'], 'execution_valid': valid,
                      'raw_execution_valid': all(states[j]['status'] == 'valid' for j in unit['raw_jobs']),
                      'raw_assessment_complete': False, 'post_assessment_complete': False,
                      'assessment_complete': False, 'terminal_status': 'review_incomplete',
                      'raw': raw, 'post_only': [], 'post_only_assessment': 'unavailable',
                      'observed_output_words': observed_words, 'output_words': observed_words if valid else None,
                      'review_gate_cause': failed.get('unresolved', [])})
    return {'case_id': case, 'status': 'not_evaluable_review_failure',
            'judgments_locked': False, 'equivalence_review_locked': False,
            'families': {}, 'units': units, 'unresolved': failed.get('unresolved', []),
            'sources': {'failed_report': failed.get('sources'), 'output_bindings': bindings},
            'claim_ceiling': 'Null assessments mean unavailable review, not zero novelty or unintelligible candidates.'}


def gate_pairs(root, kind, schedule, states, failed):
    pairs = []
    for pair in schedule[kind + '_pairs']:
        raw_ids = []
        if kind == 'p09':
            for source in pair['raw_sources']:
                candidates, _ = rows(root, source)
                raw_ids.extend(x['id'] for x in candidates)
        arms = []
        for method, job in pair['arms'].items():
            output = {'method': method, 'execution_valid': states[job]['status'] == 'valid',
                      'assessment_complete': False, 'judgment_resolved': False,
                      'terminal_status': 'review_incomplete', 'fit': None,
                      'review_reasons': ['Independent review coverage unavailable.']}
            if kind == 'p08':
                output.update({field: None for field in ['decision_relevant', 'competing_predictions',
                              'probe_feasible', 'support', 'distinct_question', 'unresolved_contradictions']})
            else:
                output['raw'] = [{'source_id': rid, 'causal_relation': None, 'discriminator': None,
                                  'uncertainty': None, 'judgment_resolved': False} for rid in raw_ids]
                output['unsupported_additions'] = []
                output['addition_assessment'] = 'unavailable'
            arms.append(output)
        pairs.append({'pair_id': pair['pair_id'], 'case_id': pair['case_id'],
                      'stratum': pair.get('stratum'), 'arms': arms,
                      'contrast_reviews': ['Independent review coverage unavailable.']})
    return {'kind': kind, 'status': 'not_evaluable_review_failure', 'judgments_locked': False,
            'pairs': pairs, 'unresolved': failed.get('unresolved', []), 'sources': failed.get('sources', {})}


def create(kind, case=None, root=R):
    root = Path(root)
    stem = 'main-' + case if kind == 'main' else kind
    source = root / 'reports' / (stem + '-resolved.json')
    failed = json.loads(source.read_text())
    if failed.get('status') != 'incomplete' or failed.get('judgments_locked') is True:
        raise ValueError('Only an explicitly incomplete review report can receive failure gates')
    spec = importlib.util.spec_from_file_location('gate_runtime', root / 'tools/runtime.py')
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    states = runtime.status()['jobs']
    schedule = json.loads((root / 'schedule.json').read_text())
    result = gate_main(root, case, schedule, states, failed) if kind == 'main' else gate_pairs(root, kind, schedule, states, failed)
    result['failed_review_report_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    output = root / 'reports' / (stem + '-gated.json')
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=['main', 'p08', 'p09'])
    parser.add_argument('case', nargs='?')
    args = parser.parse_args()
    print(create(args.kind, args.case))

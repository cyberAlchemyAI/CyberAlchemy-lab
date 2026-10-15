#!/usr/bin/env python3
"""Describe all four locked cases without selecting or retuning finalists."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]

def read(p):
    return json.loads((R / p).read_text())

def sha(p):
    return hashlib.sha256((R / p).read_bytes()).hexdigest()

def main():
    cases = ['H1', 'H2', 'H3', 'H4']
    finalists = read('finalist-freeze.json')['finalists']
    summaries = {c: read(f'reports/confirmation-{c}-summary.json') for c in cases}
    sources = []
    rows = []
    all_units = set()
    for case, summary in summaries.items():
        assert summary['case_id'] == case and summary['phase'] == 'confirmation'
        assert summary['status'] == 'descriptive_locked_case_aggregation'
        assert len(summary['units']) == 12
        for binding in summary['sources']:
            assert sha(binding['path']) == binding['sha256']
        assert len({u['unit_id'] for u in summary['units']}) == 12
        assert not all_units & {u['unit_id'] for u in summary['units']}
        all_units.update(u['unit_id'] for u in summary['units'])
        sources.append({'path': f'reports/confirmation-{case}-summary.json', 'sha256': sha(f'reports/confirmation-{case}-summary.json')})
        metadata = read(f'cases/{case}.json')
        for condition, values in summary['conditions'].items():
            unit_rows = [u for u in summary['units'] if u['condition'] == condition]
            assert len(unit_rows) == 3
            rows.append({'case_id': case, 'case_title': metadata['title'], 'partition': metadata['partition'], 'condition': condition, 'complete_exposure': values['valid_exposure'], 'complete_control_exposure': summary['complete_control_exposure'], 'qualified_whole_workflow_families': values['qualified_whole_workflow_union'], 'qualified_whole_workflow_recurrence': values['qualified_whole_workflow_recurrence'], 'qualified_A_families': values['qualified_A_union'], 'exclusive_qualified_A_candidates': values['exclusive_qualified_A_candidates'], 'exclusive_A_recurrence': values['exclusive_A_recurrence'], 'first_two_qualified_families': values['first_two_qualified_union'], 'exclusive_A_first_two_families': values['exclusive_A_first_two_union'], 'shared_Z_A_families': values['shared_Z_A_families'], 'output_words': values['output_words'], 'observed_output_words': values['observed_output_words'], 'unit_ids': [u['unit_id'] for u in unit_rows]})
    assert all_units == {f'H{i:03d}' for i in range(1, 49)}
    assert {r['condition'] for r in rows} == {'ordinary', 'creative', *finalists}
    by_operator = {}
    for operator in finalists:
        operator_rows = [r for r in rows if r['condition'] == operator]
        by_operator[operator] = {'case_ids_with_exclusive_qualified_A': [r['case_id'] for r in operator_rows if r['complete_exposure'] and r['complete_control_exposure'] and r['exclusive_qualified_A_candidates']], 'cases_with_exclusive_family_repeated_at_least_twice': [r['case_id'] for r in operator_rows if r['complete_exposure'] and r['complete_control_exposure'] and any(len(ids) >= 2 for ids in r['exclusive_A_recurrence'].values())], 'paired_case_contrasts': [{'case_id': case, **contrast} for case, summary in summaries.items() for contrast in summary['paired_case_contrasts'] if contrast['operator'] == operator]}
    retention = collections.Counter()
    unresolved = {}
    for case, summary in summaries.items():
        for unit in summary['units']:
            retention.update(unit['retention'])
        unresolved[case] = summary['unresolved']
    result = {'status': 'complete_descriptive_confirmation_comparison', 'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'finalists': finalists, 'units': len(all_units), 'cases': cases, 'case_condition_rows': rows, 'by_operator': by_operator, 'raw_retention': dict(retention), 'unresolved_by_case': unresolved, 'sources': sources, 'tool_sha256': sha('tools/compare_confirmation.py'), 'limits': ['No new advancement threshold, composite creativity score or statistical superiority claim.', 'Family IDs are local to each case; no cross-case family equivalence is inferred.', 'Repetitions are model outputs on four synthetic cases, not independent organizations or populations.', 'Qualified-set contrasts differ from the conservative exclusive A comparison against all pooled raw control families.', 'Locally new but uncertain ideas remain in source evidence; failure to qualify does not mean absence of novelty.', 'Output words are burden proxies, not equal compute or actual token use.', 'No proposed physical or operational probe was executed in the world.']}
    out = R / 'reports/confirmation-comparison.json'
    assert not out.exists(), 'Comparison already saved; no overwrite'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'output': str(out), 'units': len(all_units), 'by_operator': by_operator, 'raw_retention': dict(retention)}, indent=2))

if __name__ == '__main__':
    main()

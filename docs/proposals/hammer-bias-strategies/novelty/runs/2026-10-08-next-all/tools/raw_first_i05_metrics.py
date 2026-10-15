"""I05 parent/interface comparisons over locked native judgments only.

No new grades or family merges. Instruction-process production contrasts do
not demonstrate physical coupling or whole-workflow effectiveness.
"""
from copy import deepcopy
import raw_first_case_metrics as m
import generation_raw_first_runtime as f
import generation_runtime_v2 as g

ARMS = {'I05-ordinary', 'I05-parent-a', 'I05-parent-b',
        'I05-intact-interface', 'I05-broken-interface', 'I05-generic'}
INTACT = 'I05-intact-interface'
COMPARATORS = sorted(ARMS - {INTACT})


def interface_from_case(case, pairs):
    if case['study_id'] != 'I05' or set(case['arms']) != ARMS:
        raise ValueError('Require the complete I05 six-arm comparison')
    result = deepcopy(case)
    arms = result['arms']
    valid = result['raw_comparison_evaluable']
    cards = [c['card_id'] for c in arms[INTACT]['cards']
             if c['qualification']['status'] == 'eligible']
    comparisons = {}
    for name in COMPARATORS:
        controls = [c['card_id'] for c in arms[name]['cards']
                    if c['locked_values']['intelligible'] is not False]
        counts = {}
        for measure in ['qualified_family_bounds', 'potentially_qualified_family_bounds']:
            a, b = arms[INTACT][measure], arms[name][measure]
            counts[measure] = ([a[0] - b[1], a[1] - b[0]]
                               if valid and a is not None and b is not None else None)
        comparisons[name] = {
            'qualified_intact_card_exclusivity':
                {c: m.exclusivity(c, controls, pairs) for c in cards} if valid else None,
            'intact_minus_comparator_family_bounds': counts,
        }
    parents = [c['card_id'] for name in ['I05-parent-a', 'I05-parent-b']
               for c in arms[name]['cards']
               if c['locked_values']['intelligible'] is not False]
    result['interface_comparison'] = {
        'comparisons': comparisons,
        'distinct_from_both_parents':
            {c: m.exclusivity(c, parents, pairs) for c in cards} if valid else None,
        'physical_interface_effect_measured': False,
        'interpretation': 'Descriptive production differences and direct family '
                          'relations. A qualified intact card must differ from '
                          'intelligible parents even when their fit is partial. '
                          'An empty, missing or unresolved comparison is not a '
                          'measured interface effect.',
    }
    return result


def case_metrics(case):
    raw, _ = f.bound_lock('I05', case, 'raw')
    result = interface_from_case(m.case_metrics('I05', case),
                                 m.relation_index(raw['rows']))
    _, admin = f.bound_packet('I05', case, 'raw')
    units = {x['unit_id']: x for x in admin['mapping'] if 'unit_id' in x}
    result['raw_unit_contract_evidence'] = [
        {'arm': units[row['identity']['unit_id']]['arm_or_method'],
         'row_id': row['row_id'], 'values': row['values'],
         'field_status': row['field_status']}
        for row in raw['rows'] if row['table'] == 'unit_rows']
    result['reporter_bindings'] = [
        {'path': p, 'sha256': g.sha(f.R / p)} for p in
        ['tools/raw_first_case_metrics.py', 'tools/raw_first_i05_metrics.py']]
    return result


if __name__ == '__main__':
    import json, sys
    print(json.dumps(case_metrics(sys.argv[1]), indent=2))

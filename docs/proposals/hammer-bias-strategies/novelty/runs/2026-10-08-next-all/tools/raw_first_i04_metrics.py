"""I04 factorial arithmetic over already locked native judgments.

Generic creativity is outside the four factorial cells. No semantic grades,
family closures, experimental calls or admission gates are created here.
The original case reporter remains immutable. Independent completion audit
is still required before these aggregates can support a completed study.
"""
from copy import deepcopy
from fractions import Fraction
import raw_first_case_metrics as m
import generation_raw_first_runtime as f
import generation_runtime_v2 as g

CELLS = {
    '00': 'I04-ordinary-original',
    '10': 'I04-conversion-original',
    '01': 'I04-ordinary-relocated',
    '11': 'I04-conversion-relocated',
}
GENERIC = 'I04-generic'
WEIGHTS = {
    'conversion_main': {'00': -0.5, '10': 0.5, '01': -0.5, '11': 0.5},
    'carrier_main': {'00': -0.5, '10': -0.5, '01': 0.5, '11': 0.5},
    'conversion_by_carrier': {'00': 1, '10': -1, '01': -1, '11': 1},
}


def weighted_bounds(bounds, weights):
    """Conservative signed interval arithmetic; no independence assumption."""
    if any(bounds.get(k) is None for k in weights):
        return None
    low, high = Fraction(0), Fraction(0)
    for key, weight in weights.items():
        a, b = bounds[key]
        if not (type(a) is int and type(b) is int and 0 <= a <= b):
            raise ValueError('Invalid family count interval')
        w = Fraction(str(weight))
        low += w * (a if w >= 0 else b)
        high += w * (b if w >= 0 else a)
    return [float(low), float(high)]


def factorial_from_case(case, pairs):
    if case['study_id'] != 'I04':
        raise ValueError('This reporter applies only to I04')
    result = deepcopy(case)
    arms = result['arms']
    if set(arms) != set(CELLS.values()) | {GENERIC}:
        raise ValueError('Require exactly all four factorial cells and generic control')
    evaluable = result['raw_comparison_evaluable']
    control_names = [CELLS['00'], GENERIC]
    for name, arm in arms.items():
        eligible = [c['card_id'] for c in arm['cards']
                    if c['qualification']['status'] == 'eligible']
        primary = [c['card_id'] for c in arms[CELLS['00']]['cards']
                   if c['locked_values']['intelligible'] is not False]
        controls = [c['card_id'] for n in control_names if n != name
                    for c in arms[n]['cards']
                    if c['locked_values']['intelligible'] is not False]
        arm['primary_comparator'] = CELLS['00']
        arm['primary_exclusivity'] = ({c: m.exclusivity(c, primary, pairs)
                                      for c in eligible}
                                     if evaluable and name != CELLS['00'] else None)
        arm['secondary_ordinary_generic_overlap'] = (
            {c: m.exclusivity(c, controls, pairs) for c in eligible}
            if evaluable else None)
    combination = arms[CELLS['11']]
    parents = [c['card_id'] for n in [CELLS['10'], CELLS['01']]
               for c in arms[n]['cards']
               if c['locked_values']['intelligible'] is not False]
    combination['distinct_from_each_parent'] = (
        {c['card_id']: m.exclusivity(c['card_id'], parents, pairs)
         for c in combination['cards']
         if c['qualification']['status'] == 'eligible'} if evaluable else None)
    measurements = {}
    for measure in ['qualified_family_bounds', 'potentially_qualified_family_bounds']:
        bounds = {cell: (arms[name][measure] if evaluable else None)
                  for cell, name in CELLS.items()}
        measurements[measure] = {
            'cell_bounds': bounds,
            'contrasts': {name: weighted_bounds(bounds, weights)
                          for name, weights in WEIGHTS.items()},
        }
    result['factorial'] = {
        'cell_mapping': CELLS.copy(),
        'generic_control': GENERIC,
        'generic_included_in_factorial_contrasts': False,
        'measurements': measurements,
        'interpretation': 'Descriptive instruction-process production contrasts; '
                          'bounds retain unresolved qualification and direct family '
                          'relations. No physical interaction, statistical significance '
                          'or whole-workflow benefit is inferred.',
    }
    return result


def case_metrics(case):
    ordinary = m.case_metrics('I04', case)
    raw, _ = f.bound_lock('I04', case, 'raw')
    result = factorial_from_case(ordinary, m.relation_index(raw['rows']))
    _, admin = f.bound_packet('I04', case, 'raw')
    units = {x['unit_id']: x for x in admin['mapping'] if 'unit_id' in x}
    result['raw_unit_contract_evidence'] = [
        {'arm': units[row['identity']['unit_id']]['arm_or_method'],
         'row_id': row['row_id'], 'values': row['values'],
         'field_status': row['field_status']}
        for row in raw['rows'] if row['table'] == 'unit_rows']
    result['carrier_burden'] = {
        'human_maintenance_measured': False,
        'physical_performance_measured': False,
        'assessment': 'Conversion path, false/cancelling signals and displaced '
                      'work remain in source cards and independent locked contract '
                      'evidence; this reporter adds no new semantic assessment.',
    }
    result['reporter_bindings'] = [
        {'path': p, 'sha256': g.sha(f.R / p)} for p in
        ['tools/raw_first_case_metrics.py', 'tools/raw_first_i04_metrics.py']]
    return result


if __name__ == '__main__':
    import json, sys
    print(json.dumps(case_metrics(sys.argv[1]), indent=2))

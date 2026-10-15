"""Convergence comparisons using locked judgments; shared concerns get no
convergence creation credit. This adds arithmetic, never semantic judgments.
Independent completion audit remains required.
"""
from copy import deepcopy
import generation_raw_first_runtime as f
import generation_runtime_v2 as g
import raw_first_case_metrics as m

CONCERNS = {'concern-beneficiary', 'concern-operations', 'concern-evidence'}
TREATMENTS = {'I08-consensus', 'I08-deferred'}


def convergence_from_case(case, pairs):
    if case['study_id'] != 'I08' or set(case['arms']) != CONCERNS | TREATMENTS:
        raise ValueError('Require all three shared concerns and both convergers')
    result = deepcopy(case)
    all_arms = result['arms']
    result['shared_concerns'] = {k: all_arms[k] for k in sorted(CONCERNS)}
    result['arms'] = {k: all_arms[k] for k in sorted(TREATMENTS)}
    valid = result['raw_comparison_evaluable']
    source_cards = [c['card_id'] for name in CONCERNS
                    for c in all_arms[name]['cards']
                    if c['locked_values']['intelligible'] is not False]
    for name, arm in result['arms'].items():
        other = next(iter(TREATMENTS - {name}))
        controls = [c['card_id'] for c in all_arms[other]['cards']
                    if c['locked_values']['intelligible'] is not False]
        eligible = [c['card_id'] for c in arm['cards']
                    if c['qualification']['status'] == 'eligible']
        arm['primary_comparator'] = other
        arm['primary_exclusivity'] = (
            {c: m.exclusivity(c, controls, pairs) for c in eligible}
            if valid else None)
        arm['secondary_ordinary_generic_overlap'] = None
        arm['distinct_from_shared_concerns'] = (
            {c: m.exclusivity(c, source_cards, pairs) for c in eligible}
            if valid else None)
    contrast = {}
    for measure in ['qualified_family_bounds', 'potentially_qualified_family_bounds']:
        a = all_arms['I08-deferred'][measure]
        b = all_arms['I08-consensus'][measure]
        contrast[measure] = ([a[0] - b[1], a[1] - b[0]]
                             if valid and a is not None and b is not None else None)
    counts = result['denominators']
    counts['all_raw_source_cards'] = counts.pop('raw_cards')
    counts['shared_concern_cards'] = sum(all_arms[k]['candidate_count'] for k in CONCERNS)
    counts['convergence_raw_cards'] = sum(all_arms[k]['candidate_count'] for k in TREATMENTS)
    assert counts['all_raw_source_cards'] == counts['shared_concern_cards'] + counts['convergence_raw_cards']
    result['convergence_comparison'] = {
        'deferred_minus_consensus_family_bounds': contrast,
        'shared_concern_creation_credit': 0,
        'whole_robot_talks_or_two_lane_effect_estimated': False,
        'interpretation': 'Direct convergence production contrasts on identical '
                          'shared concern reports. Source cards remain visible '
                          'and charged once. Contradiction judgments are copied '
                          'without equating agreement or consensus with truth.',
    }
    return result


def case_metrics(case):
    raw, _ = f.bound_lock('I08', case, 'raw')
    result = convergence_from_case(m.case_metrics('I08', case),
                                   m.relation_index(raw['rows']))
    _, admin = f.bound_packet('I08', case, 'raw')
    units = {x['unit_id']: x for x in admin['mapping'] if 'unit_id' in x}
    selected = [j for j in f.case_jobs('I08', case, 'raw') if j['role'] == 'convergence']
    assert len(selected) == 2 and selected[0]['input_refs'] == selected[1]['input_refs']
    assert selected[0]['depends_on'] == selected[1]['depends_on'] and len(selected[0]['depends_on']) == 3
    result['shared_input_bindings'] = [
        {'path': p, 'sha256': g.sha(f.R / p)} for p in selected[0]['input_refs']]
    result['raw_contradiction_and_contract_evidence'] = [
        {'arm': units[row['identity']['unit_id']]['arm_or_method'],
         'row_id': row['row_id'], 'identity': row['identity'],
         'values': row['values'], 'field_status': row['field_status']}
        for row in raw['rows'] if row['table'] in ['contradiction_rows', 'unit_rows']]
    result['reporter_bindings'] = [
        {'path': p, 'sha256': g.sha(f.R / p)} for p in
        ['tools/raw_first_case_metrics.py', 'tools/raw_first_i08_metrics.py']]
    return result

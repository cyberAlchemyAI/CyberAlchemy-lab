"""Deterministic reporting of observed, locked model judgments.

No semantic grades, transitive family merges, scored calls or gates are created.
This reporter is outside the frozen executor and requires an independent audit
before its aggregates can serve as completion evidence.
"""
import json
from datetime import datetime
import generation_raw_first_runtime as f
import generation_runtime_v2 as g
from blind_generation_raw_first import canonical_hash

CHECKS = {
    'intelligible': lambda x: x is True,
    'usefulness': lambda x: type(x) is int and x >= 1,
    'observability': lambda x: type(x) is int and x == 2,
    'fit': lambda x: x == 'preserves',
    'support': lambda x: x != 'unsupported',
    'novelty': lambda x: x == 'new',
    'family_confirmed': lambda x: x is True,
    'contract': lambda x: x == 'met',
}


def qualification(row):
    failures, unresolved = [], []
    for field, check in CHECKS.items():
        status, value = row['field_status'][field], row['values'][field]
        if status not in ['agreed', 'adjudicated'] or value is None:
            unresolved.append(field)
        elif not check(value):
            failures.append({'field': field, 'locked_value': value})
    return {'status': 'ineligible' if failures else 'unresolved' if unresolved else 'eligible',
            'agreed_exclusions': failures, 'unresolved_requirements': unresolved}


def relation_index(rows):
    return {frozenset([r['identity']['card_a'], r['identity']['card_b']]): r
            for r in rows if r['table'] == 'candidate_pairs'}


def pair_relation(a, b, pairs):
    if a == b:
        return 'equivalent'
    row = pairs.get(frozenset([a, b]))
    if row is None or row['field_status']['relation'] not in ['agreed', 'adjudicated']:
        return None
    return row['values']['relation']


def family_bounds(ids, pairs):
    """Within a single arm, at most two live cards; no graph closure."""
    assert len(ids) <= 2
    if len(ids) < 2:
        return [len(ids), len(ids)]
    relation = pair_relation(*ids, pairs)
    return [1, 1] if relation in ['equivalent', 'parameter'] else [2, 2] if relation == 'distinct' else [1, 2]


def exclusivity(card, controls, pairs):
    relations = [{'control_card': x, 'locked_relation': pair_relation(card, x, pairs)} for x in controls]
    status = ('not_exclusive' if any(x['locked_relation'] in ['equivalent', 'parameter'] for x in relations)
              else 'unresolved' if any(x['locked_relation'] != 'distinct' for x in relations)
              else 'exclusive')
    return {'status': status, 'comparisons': relations}


def case_metrics(study, case):
    f.ready()
    raw, raw_witness = f.bound_lock(study, case, 'raw')
    post, post_witness = f.bound_lock(study, case, 'post')
    _, admin = f.bound_packet(study, case, 'raw')
    units = {x['job_id']: x for x in admin['mapping'] if 'unit_id' in x}
    cards = {x['opaque_id']: x for x in admin['mapping'] if 'opaque_id' in x and x['field'] == 'openings'}
    raw_rows = [x for x in raw['rows'] if x['table'] == 'raw_rows']
    pairs = relation_index(raw['rows'])
    prior = {(x['table'], x['row_id']): x for x in raw['rows']}
    current = {(x['table'], x['row_id']): x for x in post['rows']}
    assert all(canonical_hash(current[k]['values']) == canonical_hash(v['values']) and current[k]['field_status'] == v['field_status'] for k, v in prior.items())
    all_jobs = f.case_jobs(study, case)
    job_ids = {x['job_id'] for x in all_jobs}
    review_ids = {j['job_id'] for j in f.jobs().values() if j['study_id'] == study and j['case_id'] == case}
    events = g.events()
    starts = [e for e in events if e['event_kind'] == 'native_spawn' and e.get('job_id') in job_ids | review_ids]
    terminals = [e for e in events if e['event_kind'] == 'native_terminal_join' and e.get('job_id') in job_ids | review_ids]
    assert all(e.get('terminal_observed') is True for e in terminals)
    assert len({e['job_id'] for e in terminals}) == len(terminals)
    d_ids = {x['job_id'] for x in all_jobs if x['role'] == 'compression'}
    d_prepared = [e for e in events if e['event_kind'] == 'job_prepared' and e.get('job_id') in d_ids]
    assert all(datetime.fromisoformat(e['time_utc']) > datetime.fromisoformat(raw_witness['time_utc']) for e in d_prepared)
    raw_valid = all(g.status()[x['job_id']] == 'valid' for x in all_jobs if x['role'] != 'compression')
    evaluable = raw_valid and raw['independent_review_complete']
    arms = {}
    for row in raw_rows:
        card = row['identity']['card_id']; mapping = cards[card]; unit = units[mapping['job_id']]
        arm = arms.setdefault(unit['arm_or_method'], {'job_id': mapping['job_id'], 'shared_seed': unit['role'] == 'incumbent-seed', 'cards': []})
        arm['cards'].append({'card_id': card, 'local_id': mapping['local_id'], 'qualification': qualification(row), 'locked_values': row['values'], 'field_status': row['field_status']})
    # Include observed empty/invalid arms in denominators, with null credit.
    for job, unit in units.items():
        arms.setdefault(unit['arm_or_method'], {'job_id': job, 'shared_seed': unit['role'] == 'incumbent-seed', 'cards': []})
    primary_name = study + ('-critique' if study == 'I03' else '-ordinary')
    for name, arm in arms.items():
        eligible = [x['card_id'] for x in arm['cards'] if x['qualification']['status'] == 'eligible']
        unresolved = [x['card_id'] for x in arm['cards'] if x['qualification']['status'] == 'unresolved']
        arm.update(execution=g.status()[arm['job_id']], candidate_count=len(arm['cards']), qualified_card_count=len(eligible) if evaluable else None,
                   qualification_unresolved_card_count=len(unresolved) if evaluable else None,
                   qualified_family_bounds=family_bounds(eligible, pairs) if evaluable else None,
                   potentially_qualified_family_bounds=[family_bounds(eligible, pairs)[0], len(eligible) + len(unresolved)] if evaluable else None)
        arm['no_opening'] = g.status()[arm['job_id']] == 'valid' and not arm['cards']
        controls = [x['card_id'] for other_name, other in arms.items() if other_name.endswith(('-ordinary', '-generic')) and other_name != name
                    for x in other['cards'] if x['locked_values']['intelligible'] is not False]
        arm['secondary_ordinary_generic_overlap'] = {card: exclusivity(card, controls, pairs) for card in eligible} if evaluable else None
        primary = [x['card_id'] for x in arms.get(primary_name, {}).get('cards', []) if x['locked_values']['intelligible'] is not False]
        arm['primary_comparator'] = primary_name
        arm['primary_exclusivity'] = {card: exclusivity(card, primary, pairs) for card in eligible} if evaluable and name != primary_name else None
    retention = [x for x in post['rows'] if x['table'] == 'retention_rows']
    retained = [x for x in retention if x['values']['relation'] == 'retained' and x['values']['discriminator'] == 'retained' and x['values']['uncertainty'] == 'retained'
                and all(x['values'][k] is True for k in ['lineage_consistent', 'fit_preserved', 'complete_protected_fields'])
                and all(v in ['agreed', 'adjudicated'] for v in x['field_status'].values())]
    refs = {f.ref(study, case, phase, kind) for phase in ['raw', 'post'] for kind in ['packet', 'map', 'lock']}
    refs |= {e['output_ref'] for e in terminals if (f.R / e['output_ref']).exists()}
    overages = []
    for e in terminals:
        limit = 6000 if e['job_id'] in review_ids else 350 if e['job_id'] in d_ids else 420
        words = e['validation'].get('saved_words')
        if words is not None and words > limit:
            overages.append({'job_id': e['job_id'], 'saved_words': words, 'soft_limit': limit, 'excess_words': words - limit})
    return {'study_id': study, 'case_id': case, 'meaning': 'Arithmetic over actual locked model judgments; no new semantic grades or family merges',
            'raw_execution_valid': raw_valid, 'raw_independent_review_complete': raw['independent_review_complete'], 'raw_comparison_evaluable': evaluable,
            'post_independent_review_complete': post['independent_review_complete'], 'arms': arms,
            'denominators': {'planned_generation_roles': len(all_jobs), 'planned_review_roles': len(review_ids), 'actual_native_starts': len(starts),
                             'actual_terminal_joins': len(terminals), 'structurally_valid_terminal_outputs': sum(e['validation']['valid'] for e in terminals),
                             'invalid_terminal_outputs': sum(not e['validation']['valid'] for e in terminals), 'skipped_roles': sum(g.status()[k] == 'skipped' for k in job_ids),
                             'raw_cards': len(raw_rows), 'post_retention_rows': len(retention)},
            'fully_retained_rows': len(retained) if post['independent_review_complete'] else None,
            'post_addition_rows': [x for x in post['rows'] if x['table'] == 'addition_rows'],
            'raw_lock_time_utc': raw_witness['time_utc'], 'first_D_preparation_time_utc': min((e['time_utc'] for e in d_prepared), default=None),
            'exact_carried_raw_rows': len(raw['rows']), 'carried_independent_grade_credit': 0,
            'raw_scalar_unresolved': raw['unresolved_scalar_count'], 'raw_family_unresolved': raw['family_unresolved_count'],
            'post_uncertainty_by_origin': post['uncertainty_counts_by_origin'], 'saved_words_proxy': sum(e['validation'].get('saved_words', 0) for e in terminals),
            'soft_word_overages': overages, 'source_bindings': [{'path': p, 'sha256': f.sha(f.R / p)} for p in sorted(refs)]}


if __name__ == '__main__':
    import sys
    print(json.dumps(case_metrics(*sys.argv[1:3]), indent=2))

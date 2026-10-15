"""UNADMITTED v4 deterministic P10 views; no new candidates or semantic grades.

Unlike the earlier unadmitted draft, a resolved family_confirmed=False is
not an unresolved ranking key: it excludes eligibility, not ordinary display.
Unresolved within-pool family relations still gate both views.
"""
FIT = {'preserves': 0, 'uncertain': 1, 'conditional': 2, 'violates': 3}
REQUIRED = ['id', 'fit', 'usefulness', 'observability', 'intelligible', 'support',
            'novelty', 'retention', 'family_id', 'family_confirmed',
            'uncertain_links', 'raw_order']


def views(candidates, context_complete=True):
    if not context_complete:
        return {'status': 'not_evaluable', 'cause': 'incomplete_execution_or_dual_review_context',
                'ordinary': None, 'alternative': None}
    missing = [c.get('id') for c in candidates
               if any(k not in c or c[k] is None for k in REQUIRED)]
    if missing or any(c['uncertain_links'] or c['retention'] in ['uncertain', 'unobservable']
                      for c in candidates):
        return {'status': 'not_evaluable', 'cause': 'unresolved_ranking_retention_or_family_fields',
                'candidate_ids': missing, 'ordinary': None, 'alternative': None}
    if len({c['id'] for c in candidates}) != len(candidates):
        raise ValueError('Candidate IDs must be unique')
    pool = sorted(candidates, key=lambda c: (FIT[c['fit']], -c['usefulness'],
                                            -c['observability'], c['raw_order'], c['id']))
    retained = [c for c in pool if c['retention'] == 'retained']
    ordinary = []
    for c in retained:
        if all(c['family_id'] != x['family_id'] for x in ordinary):
            ordinary.append(c)
        if len(ordinary) == 2:
            break
    eligible = [c for c in retained if c['intelligible'] is True and c['novelty'] == 'new'
                and c['usefulness'] >= 1 and c['observability'] == 2
                and c['fit'] == 'preserves' and c['support'] != 'unsupported'
                and c['family_confirmed'] is True and c.get('contract') is not None]
    alternative = list(ordinary)
    if ordinary:
        others = [c for c in eligible if c['family_id'] != ordinary[0]['family_id']]
        if others:
            alternative = [ordinary[0], others[0]]
    ids = lambda cs: [c['id'] for c in cs]
    oi, ai = ids(ordinary), ids(alternative)
    return {'status': 'evaluable', 'ordinary': oi, 'alternative': ai,
            'first_unchanged': oi[:1] == ai[:1], 'eligible_ids': ids(eligible),
            'entering_ids': [x for x in ai if x not in oi],
            'displaced_ids': [x for x in oi if x not in ai],
            'same_candidate_pool': True, 'eligible_absence_is_not_failure': not bool(eligible),
            'claim': 'Deterministic exposure only; no human decision value measured.'}

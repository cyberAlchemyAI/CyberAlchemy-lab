"""UNADMITTED I10 source adapter. Reuses exact I06 pools, adds no judgments.

All eight planned pools must be saved after prospective admission. This module
does not save results, grant gates or assert study completion.
"""
import json
import generation_raw_first_runtime as f
import generation_runtime_v2 as g
import raw_first_case_metrics as m
import presentation_v3 as p

CASES = ['H-C1', 'H-C2', 'A-C1', 'A-C2']
ARMS = ['I06-ordinary', 'I06-backcast']
RESOLVED = {'agreed', 'adjudicated'}


def retention_status(row):
    if row is None or any(s not in RESOLVED for s in row['field_status'].values()):
        return 'unobservable' if row is None else 'uncertain'
    values = row['values']
    fields = ['relation', 'discriminator', 'uncertainty']
    flags = ['lineage_consistent', 'fit_preserved', 'complete_protected_fields']
    if all(values[k] == 'retained' for k in fields) and all(values[k] is True for k in flags):
        return 'retained'
    if any(values[k] == 'lost' for k in fields) or any(values[k] is False for k in flags):
        return 'lost'
    return 'uncertain'


def pool(case_id, arm):
    if case_id not in CASES or arm not in ARMS:
        raise ValueError('Only the eight originally scheduled I10 pools')
    metric = m.case_metrics('I06', case_id)
    raw, _ = f.bound_lock('I06', case_id, 'raw')
    post, _ = f.bound_lock('I06', case_id, 'post')
    selected = metric['arms'][arm]
    source_job = g.jobs()[selected['job_id']]
    source = f.read(f.R / source_job['output_ref'])
    cards = selected['cards']
    assert len(cards) <= 2, 'Preserve the frozen per-arm capacity'
    assert {c['local_id'] for c in cards} == {c['id'] for c in source['openings']}
    order = {c['id']: i for i, c in enumerate(source['openings'])}
    originals = {c['id']: c for c in source['openings']}
    relations = m.relation_index(raw['rows'])
    relation = m.pair_relation(cards[0]['card_id'], cards[1]['card_id'], relations) if len(cards) == 2 else 'distinct'
    uncertain_pair = relation not in ['equivalent', 'parameter', 'distinct']
    retention = {row['identity']['source_card_id']: row for row in post['rows']
                 if row['table'] == 'retention_rows'}
    candidates, evidence = [], []
    for c in cards:
        values = {k: c['locked_values'][k] if c['field_status'][k] in RESOLVED else None
                  for k in ['fit', 'usefulness', 'observability', 'intelligible', 'support',
                            'novelty', 'contract', 'family_confirmed']}
        source_id = selected['job_id'] + ':' + c['local_id']
        family_id = min(x['card_id'] for x in cards) if relation in ['equivalent', 'parameter'] else c['card_id']
        values.update(id=source_id, family_id=family_id, uncertain_links=uncertain_pair,
                      raw_order=order[c['local_id']], retention=retention_status(retention.get(c['card_id'])))
        candidates.append(values)
        evidence.append({'source_id': source_id, 'opaque_card_id': c['card_id'],
                         'raw_payload': originals[c['local_id']],
                         'locked_raw_values': c['locked_values'], 'field_status': c['field_status'],
                         'locked_retention_row': retention.get(c['card_id'])})
    complete = (metric['raw_execution_valid'] and metric['raw_independent_review_complete']
                and metric['post_independent_review_complete']
                and metric['denominators']['invalid_terminal_outputs'] == 0)
    view = p.views(candidates, context_complete=complete)
    by_id = {c['id']: c for c in candidates}
    raw_payload = {x['source_id']: x['raw_payload'] for x in evidence}
    burdens = {}
    for name in ['ordinary', 'alternative']:
        ids = view[name]
        burdens[name] = (None if ids is None else {
            'selected_raw_full_text_saved_words': sum(len(json.dumps(raw_payload[x], ensure_ascii=False).split()) for x in ids),
            'family_exposure': len({by_id[x]['family_id'] for x in ids}),
            'eligible_exposure': sum(x in view['eligible_ids'] for x in ids),
            'selected_scores_and_contracts': [by_id[x] for x in ids]})
    refs = {x['path']: x for x in metric['source_bindings']}
    for path in ['tools/i10_source_pool_v3.py', 'tools/presentation_v3.py',
                 'tools/raw_first_case_metrics.py', 'criteria.json', 'inputs/plan/PLAN.md',
                 'inputs/plan/portfolio.json']:
        refs[path] = {'path': path, 'sha256': g.sha(f.R / path)}
    return {'case_id': case_id, 'generation_arm': arm, 'source_job_id': selected['job_id'],
            'same_locked_candidate_pool': True, 'new_generation_or_review_call_credit': 0,
            'full_ordinary_generic_upstream_context_preserved': True,
            'candidates': candidates, 'source_evidence': evidence, 'views': view,
            'full_text_burden': burdens,
            'entering_and_displaced_scores_contracts': {
                k: [by_id[x] for x in view.get(k, [])] for k in ['entering_ids', 'displaced_ids']},
            'source_bindings': sorted(refs.values(), key=lambda x: x['path']),
            'claim': 'Deterministic exposure only; no human decision benefit measured.'}

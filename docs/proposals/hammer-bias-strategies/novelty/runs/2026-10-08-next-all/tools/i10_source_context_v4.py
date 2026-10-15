"""Unscored source verification, separate from I10 view execution.

Reconcile all six generation/compression and four review roles for each proper
I06 confirmation case. Never supply semantic grades or construct a view here.
"""
from pathlib import Path
import generation_raw_first_runtime as f
import generation_runtime_v2 as g
import blind_generation_v2 as b
from blind_generation_raw_first import canonical_hash

CASES = ['H-C1', 'H-C2', 'A-C1', 'A-C2']
WITNESS = 'receipts/I10-source-context-witness.v4.json'


def stage_coverage(generation_states, review_states, events):
    required = set(generation_states) | set(review_states)
    starts = [e for e in events if e.get('job_id') in required and e['event_kind'] == 'native_spawn']
    terminals = [e for e in events if e.get('job_id') in required and e['event_kind'] == 'native_terminal_join']
    start_ids = [e['job_id'] for e in starts]
    terminal_ids = [e['job_id'] for e in terminals]
    all_states = {**generation_states, **review_states}
    exact_starts = len(start_ids) == len(required) and set(start_ids) == required
    exact_terminals = len(terminal_ids) == len(required) and set(terminal_ids) == required
    valid_terminals = all(e.get('terminal_observed') is True and e['validation']['valid'] is True
                          for e in terminals)
    valid_states = all(x == 'valid' for x in all_states.values())
    return {'complete': bool(required) and exact_starts and exact_terminals and valid_terminals and valid_states,
            'required_generation_roles': len(generation_states), 'required_review_roles': len(review_states),
            'actual_native_starts': len(starts), 'actual_terminal_joins': len(terminals),
            'exact_start_coverage': exact_starts, 'exact_terminal_coverage': exact_terminals,
            'all_required_states_valid': valid_states, 'all_observed_terminals_valid': valid_terminals,
            'structurally_valid_terminals': sum(e['validation']['valid'] is True for e in terminals),
            'skipped_roles': sorted(k for k, v in all_states.items() if v == 'skipped'),
            'invalid_roles': sorted(k for k, v in all_states.items() if v == 'invalid'),
            'missing_or_unfinished_roles': sorted(k for k, v in all_states.items() if v not in ['valid', 'invalid', 'skipped'])}


def case_record(case_id):
    if case_id not in CASES:
        raise ValueError('Only proper I06 confirmation sources')
    f.ready()
    raw, raw_witness = f.bound_lock('I06', case_id, 'raw')
    post, post_witness = f.bound_lock('I06', case_id, 'post')
    raw_packet, admin = f.bound_packet('I06', case_id, 'raw')
    _, post_admin = f.bound_packet('I06', case_id, 'post')
    jobs = f.case_jobs('I06', case_id)
    reviews = [j for j in f.jobs().values() if j['study_id'] == 'I06' and j['case_id'] == case_id]
    required = {j['job_id'] for j in jobs + reviews}
    events = [e for e in g.events() if e.get('job_id') in required or
              (e.get('study_id') == 'I06' and e.get('case_id') == case_id and
               e['event_kind'] in ['raw_first_packet', 'raw_first_lock'])]
    gs, rs = g.status(), f.review_status()
    stage = stage_coverage({j['job_id']: gs[j['job_id']] for j in jobs},
                           {j['job_id']: rs[j['job_id']] for j in reviews}, events)
    bindings = {x['path']: x for x in admin['input_bindings'] + post_admin['input_bindings']
                + raw['source_bindings'] + post['source_bindings']}
    for phase in ['raw', 'post']:
        for kind in ['packet', 'map', 'lock']:
            path = f.ref('I06', case_id, phase, kind)
            bindings[path] = {'path': path, 'sha256': g.sha(f.R / path)}
    for e in events:
        if e['event_kind'] == 'job_prepared':
            f.bindings_valid(e['input_bindings'])
            assert g.sha(f.R / e['prompt_ref']) == e['prompt_sha256']
            bindings.update({x['path']: x for x in e['input_bindings']})
            bindings[e['prompt_ref']] = {'path': e['prompt_ref'], 'sha256': e['prompt_sha256']}
        if e['event_kind'] == 'native_terminal_join':
            assert e['terminal_observed'] is True
            path = e['output_ref']
            if (f.R / path).exists():
                assert g.sha(f.R / path) == e['validation']['output_sha256']
                bindings[path] = {'path': path, 'sha256': e['validation']['output_sha256']}
            else:
                assert e['validation']['valid'] is False
    raw_jobs = [j for j in jobs if j['role'] != 'compression']
    units = {x['job_id']: x for x in admin['mapping'] if 'unit_id' in x}
    assert set(units) == {j['job_id'] for j in raw_jobs}
    assert {x['arm_or_method'] for x in units.values()} == {'I06-ordinary', 'I06-backcast', 'I06-generic'}
    card_map = {(x['job_id'], x['local_id']): x for x in admin['mapping']
                if x.get('field') == 'openings'}
    orders = {}
    for j in raw_jobs:
        source = f.read(f.R / j['output_ref'])
        openings = source['openings']
        assert len(openings) <= 2 and len({x['id'] for x in openings}) == len(openings)
        assert {local for job, local in card_map if job == j['job_id']} == {x['id'] for x in openings}
        packet_unit = next(x for x in raw_packet['units'] if x['unit_id'] == units[j['job_id']]['unit_id'])
        assert {x['id'] for x in packet_unit['artifact']['openings']} == {
            b.card_id(j['job_id'], x['id']) for x in openings}
        assert {row['identity']['card_id'] for row in raw['rows'] if row['table'] == 'raw_rows' and
                row['identity']['card_id'] in {x['id'] for x in packet_unit['artifact']['openings']}} == {
            x['id'] for x in packet_unit['artifact']['openings']}
        orders[j['job_id']] = []
        for i, opening in enumerate(openings):
            mapping = card_map[j['job_id'], opening['id']]
            assert mapping['index'] == i and mapping['opaque_id'] == b.card_id(j['job_id'], opening['id'])
            orders[j['job_id']].append({'local_id': opening['id'], 'frozen_source_order': i,
                                       'source_payload_sha256': canonical_hash(opening)})
    protected = {f'cases/{case_id}.json', 'archives/case-archives.json',
                 'criteria-generation.v2.json', 'generation-review-contract.v2.json'}
    assert protected <= set(bindings)
    f.bindings_valid(list(bindings.values()))
    return {'case_id': case_id, 'stage_coverage': stage, 'source_orders': orders,
            'raw_independent_review_complete': raw['independent_review_complete'],
            'post_independent_review_complete': post['independent_review_complete'],
            'case_events': events, 'ordinary_generic_full_source_context_verified': True,
            'source_bindings': sorted(bindings.values(), key=lambda x: x['path']),
            'raw_lock_sha256': raw_witness['output_sha256'], 'post_lock_sha256': post_witness['output_sha256']}


def source_context(case_id):
    witness = f.read(f.R / WITNESS)
    f.bindings_valid(witness['source_bindings'])
    observed = case_record(case_id)
    assert canonical_hash(observed) == canonical_hash(witness['cases'][case_id]), 'I06 source/event witness drift'
    return observed

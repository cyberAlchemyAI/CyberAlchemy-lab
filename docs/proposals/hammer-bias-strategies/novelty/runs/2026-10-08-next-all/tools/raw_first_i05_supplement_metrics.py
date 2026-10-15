"""Report a separate observed scalar resolution without revising raw snapshots.

The original raw/post judgment carry stays exact. This adds the single permitted
native scalar turn to burden and reports its arithmetic separately. It cannot
resolve family links or supply semantic judgments.
"""
from copy import deepcopy
from datetime import datetime
import generation_raw_first_runtime as f
import generation_runtime_v2 as g
import generation_disputes_v2 as d
import raw_first_case_metrics as m
import raw_first_i05_metrics as i05
from blind_generation_raw_first import canonical_hash


def validate_resolution(original, resolved, adjudication):
    checked = d.adjudication_valid(original, adjudication)
    assert checked['valid'], checked['errors']
    decisions = {x['dispute_id']: x for x in adjudication['resolutions']}
    changes = {}
    for item in original['disputes']:
        decision = decisions[item['dispute_id']]
        if decision['status'] == 'resolved':
            key = (item['table'], item['row_id'], item['field'])
            assert (item['table'], item['field']) not in d.FAMILY
            changes[key] = decision['value']
    assert len(original['rows']) == len(resolved['rows'])
    for a, b in zip(original['rows'], resolved['rows']):
        assert (a['table'], a['row_id'], a['identity']) == (b['table'], b['row_id'], b['identity'])
        assert set(a['values']) == set(b['values'])
        assert set(a['field_status']) == set(b['field_status'])
        for field, value in a['values'].items():
            key = (a['table'], a['row_id'], field)
            if key in changes:
                assert a['field_status'][field] == 'scalar_unresolved'
                assert canonical_hash(b['values'][field]) == canonical_hash(changes[key])
                assert b['field_status'][field] == 'adjudicated'
            else:
                assert canonical_hash(b['values'][field]) == canonical_hash(value)
                if field in a['field_status']:
                    assert b['field_status'][field] == a['field_status'][field]
    assert original['family_disagreements'] == resolved['family_disagreements']
    assert original['disputes'] == resolved['disputes']
    assert original['source_bindings'] == resolved['source_bindings']
    return len(changes)


def resolved_assessment(base, rows):
    result = deepcopy(base)
    indexed = {row['identity']['card_id']: row for row in rows if row['table'] == 'raw_rows'}
    pairs = m.relation_index(rows)
    valid = result['raw_comparison_evaluable']
    for arm in result['arms'].values():
        for card in arm['cards']:
            row = indexed[card['card_id']]
            card.update(qualification=m.qualification(row), locked_values=row['values'], field_status=row['field_status'])
        eligible = [c['card_id'] for c in arm['cards'] if c['qualification']['status'] == 'eligible']
        uncertain = [c['card_id'] for c in arm['cards'] if c['qualification']['status'] == 'unresolved']
        arm.update(qualified_card_count=len(eligible) if valid else None,
                   qualification_unresolved_card_count=len(uncertain) if valid else None,
                   qualified_family_bounds=m.family_bounds(eligible, pairs) if valid else None,
                   potentially_qualified_family_bounds=[m.family_bounds(eligible, pairs)[0], len(eligible) + len(uncertain)] if valid else None)
    for name, arm in result['arms'].items():
        eligible = [c['card_id'] for c in arm['cards'] if c['qualification']['status'] == 'eligible']
        controls = [c['card_id'] for other, values in result['arms'].items()
                    if other.endswith(('-ordinary', '-generic')) and other != name
                    for c in values['cards'] if c['locked_values']['intelligible'] is not False]
        arm['secondary_ordinary_generic_overlap'] = {c: m.exclusivity(c, controls, pairs) for c in eligible} if valid else None
        ordinary = [c['card_id'] for c in result['arms']['I05-ordinary']['cards'] if c['locked_values']['intelligible'] is not False]
        arm['primary_exclusivity'] = {c: m.exclusivity(c, ordinary, pairs) for c in eligible} if valid and name != 'I05-ordinary' else None
    return i05.interface_from_case(result, pairs)


def case_metrics(case):
    base = i05.case_metrics(case)
    original, witness = f.bound_lock('I05', case, 'raw')
    events = g.events()
    locks = [e for e in events if e['event_kind'] == 'supplementary_raw_scalar_lock'
             and e.get('study_id') == 'I05' and e.get('case_id') == case]
    assert len(locks) == 1, 'One observed separate scalar lock required'
    event = locks[0]
    assert event['original_raw_lock_sha256'] == witness['output_sha256']
    assert f.sha(f.R / event['output_ref']) == event['output_sha256']
    resolved = f.read(f.R / event['output_ref'])
    f.bindings_valid(resolved['source_bindings'])
    assert resolved['study_id'] == 'I05' and resolved['case_id'] == case
    assert resolved['original_raw_lock_binding'] == {
        'path': f.ref('I05', case, 'raw', 'lock'), 'sha256': witness['output_sha256']}
    job = event['adjudication_job_id']
    starts = [e for e in events if e['event_kind'] == 'native_spawn' and e.get('job_id') == job]
    joins = [e for e in events if e['event_kind'] == 'native_terminal_join' and e.get('job_id') == job]
    assert len(starts) == len(joins) == 1
    terminal = joins[0]
    assert terminal['terminal_observed'] is True and terminal['validation']['valid']
    assert starts[0]['agent_handle'] == terminal['agent_handle']
    assert resolved['adjudication']['output_ref'] == terminal['output_ref']
    assert f.sha(f.R / terminal['output_ref']) == terminal['validation']['output_sha256']
    prepared = [e for e in events if e['event_kind'] == 'job_prepared' and e.get('job_id') == job]
    assert len(prepared) == 1
    f.bindings_valid(prepared[0]['input_bindings'])
    assert f.sha(f.R / prepared[0]['prompt_ref']) == prepared[0]['prompt_sha256']
    assert datetime.fromisoformat(terminal['time_utc']) < datetime.fromisoformat(event['time_utc'])
    d_ids = {x['job_id'] for x in f.case_jobs('I05', case) if x['role'] == 'compression'}
    d_starts = [e for e in events if e['event_kind'] == 'native_spawn' and e.get('job_id') in d_ids]
    assert all(datetime.fromisoformat(e['time_utc']) > datetime.fromisoformat(event['time_utc']) for e in d_starts)
    body = f.read(f.R / terminal['output_ref'])
    count = validate_resolution(original, resolved, body)
    assessment = resolved_assessment(base, resolved['rows'])
    assessment['raw_scalar_unresolved'] = resolved['unresolved_scalar_count']
    assessment['raw_family_unresolved'] = resolved['family_unresolved_count']
    assessment['raw_unit_contract_evidence'] = [
        {'row_id': row['row_id'], 'identity': row['identity'], 'values': row['values'], 'field_status': row['field_status']}
        for row in resolved['rows'] if row['table'] == 'unit_rows']
    # Nested assessment concerns only final raw qualification and interfaces.
    # Retention and original carry values always refer to the original snapshot.
    keys = ['arms', 'interface_comparison', 'raw_scalar_unresolved',
            'raw_family_unresolved', 'raw_unit_contract_evidence']
    words = terminal['validation']['saved_words']
    result = {'study_id': 'I05', 'case_id': case,
              'original_snapshot': base,
              'resolved_raw_assessment': {k: assessment[k] for k in keys},
              'resolved_scalar_fields': count,
              'original_raw_post_carry_exact': True,
              'post_retention_assessment_uses': 'original_snapshot',
              'supplemental_resolution_time_utc': event['time_utc'],
              'supplemental_resolution_before_all_D_starts': True,
              'denominators': deepcopy(base['denominators']),
              'saved_words_proxy': base['saved_words_proxy'] + words,
              'soft_word_overages': deepcopy(base['soft_word_overages']),
              'source_bindings': list(base['source_bindings']) + [
                  {'path': event['output_ref'], 'sha256': event['output_sha256']},
                  {'path': terminal['output_ref'], 'sha256': terminal['validation']['output_sha256']},
                  {'path': prepared[0]['prompt_ref'], 'sha256': prepared[0]['prompt_sha256']},
                  *prepared[0]['input_bindings']],
              'reporter_bindings': list(base['reporter_bindings']) + [
                  {'path': 'tools/raw_first_i05_supplement_metrics.py', 'sha256': f.sha(f.R / 'tools/raw_first_i05_supplement_metrics.py')}],
              'meaning': 'Observed scalar-only resolution and arithmetic. No original raw/post snapshot rewrite, new family grade, or physical interface efficacy claim. Independent completion audit pending.'}
    for key in ['actual_native_starts', 'actual_terminal_joins', 'structurally_valid_terminal_outputs']:
        result['denominators'][key] += 1
    result['denominators']['actual_scalar_adjudication_roles'] = 1
    if words > 6000:
        result['soft_word_overages'].append({'job_id': job, 'saved_words': words, 'soft_limit': 6000, 'excess_words': words - 6000})
    result['source_bindings'] = list({x['path']: x for x in result['source_bindings']}.values())
    return result


if __name__ == '__main__':
    import json, sys
    print(json.dumps(case_metrics(sys.argv[1]), indent=2))

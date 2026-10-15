"""Unrun successor coverage for actual REVIEW4/5 gaps; no admission or calls.

Root integrates jobs/base_job/payload/validate into a prospectively frozen
adapter. Original sources, outputs and first review disagreements are untouched.
"""
import copy
import hashlib
from ac_runtime import read, sha, require, encoded


HELPER_SOURCES = (
    'tools/ac_review4_coverage.py',
    'coverage/REVIEW4-COVERAGE-DESIGN.v1.md',
    '../2026-10-08-process-all/STRATEGIES.md',
    '../2026-10-08-process-all/PROTOCOL.md',
    '../2026-10-08-process-all/criteria.json',
)


def jobs(r):
    require(all(r.state('REVIEW-' + str(group) + '-' + str(i))['valid']
                for group in [4, 5] for i in [1, 2]),
            'Both actual first REVIEW4 and REVIEW5 records are required')
    out = []

    def clone(source, jid, arm, method, dependencies, instructions, **flags):
        j = copy.deepcopy(r.job(source))
        j.update(job_id=jid, arm=arm, method_id=method,
                 dependencies=dependencies, instructions=instructions,
                 additional_control_coverage=True, review4_coverage=True,
                 **flags)
        out.append(j)
        return j

    for arm, method in [('MATCHED_OLD', 'CORE:S01'), ('MATCHED_O', 'O')]:
        prefix = 'COV-AC13-' + arm
        for stage in ['proposal', 'critique', 'builder']:
            deps = [] if stage == 'proposal' else [prefix + '-' +
                    ('proposal' if stage == 'critique' else 'critique')]
            clone('AC13-OLD-J0-' + stage, prefix + '-' + stage, arm,
                  method, deps,
                  'New matched interval-absence control on unchanged J0. '
                  'The exact assigned predicate is intact H unavailable at '
                  'every required hold tick, while retention and removal '
                  'requirements remain unchanged. H is initially present; '
                  'licensed detachment and H-origin M/S remain permitted. '
                  'This is not initial absence or a ban on every H-origin '
                  'part. Setup use outside the holding interval must be '
                  'disclosed and cannot refute a separate tap-use necessity. '
                  'Use only the assigned older deprivation or routine method, '
                  'without adding the AC13 logic checklist. Do not browse '
                  'original treatment or control answers. Declare six search '
                  'slots; preserve supported refusal. Use python3 exclusive '
                  'first save.', matched_interval_absence=True)

    require(r.state('AC14-IMMEDIATE-exchange')['valid'],
            'Unchanged original P08 immediate exchange must be valid')
    clone('AC14-IMMEDIATE-builder', 'COV-AC14-P08-builder', 'P08_ENDPOINT',
          'P:P08', ['AC14-IMMEDIATE-exchange'],
          'Later older-method endpoint using the unchanged valid original '
          'P08 immediate exchange. Apply P08, preserve its actual absence '
          'of contradictory required predictions, and carry source-bound '
          'no-opening rather than invent dissent, future demand, a belief, '
          'or a Q result. A recovered initial schedule is not a tension '
          'addition. Preserve the three original P08 upstream roles as '
          'correlated received evidence. Declare the same six-slot allowance '
          'and at-most-one construction; report actual spending honestly. '
          'This later endpoint is not four fresh P08 stages or equal spent '
          'work. Use python3.', p08_later_endpoint=True)

    clone('AC15-O-selection', 'COV-AC15-routine-selection', 'ROUTINE', 'O', [],
          'Routine fixed-pool selection with no frontier or novelty-reserved '
          'slot. Rate all six immutable entries and rank hard-feasible '
          'implementations by lower non-idle action burden, then immutable '
          'pool order. Retain at most two; keep at most one supported '
          'investigation separately. Originality may be recorded but does '
          'not choose or displace an implementation. No pool enlargement, '
          'schedule rewriting, invented measurement or new construction. '
          'Declare six comparison slots before work. Use python3.',
          routine_selection=True)
    clone('AC15-OLD-selection', 'COV-AC15-P10-selection', 'P10', 'P:P10',
          ['COV-AC15-routine-selection'],
          'Apply the supplied literal historical P10 visible-alternative '
          'operation to the immutable pool and the actual saved routine '
          'ratings. Keep every rating byte-equivalent and the ordinary '
          'first choice unchanged. Produce ordinary and alternative views, '
          'entering/displaced identities, unchanged assessments, qualification '
          'or fallback reasons, uncertainty and added text burden. Do not '
          'invent missing historical rubric fields or claim original '
          'two-review/equivalence gates passed when their lock evidence is '
          'absent. Distinguish a native qualitative adaptation from exact '
          'legacy ranking reproduction; retain an unavailable eligibility '
          'decision where necessary. No new generation. Use python3.',
          p10_selection=True)

    pfx = 'COV-AC16-PRACTICED_OLD-'
    for stage, case in [('practice1', 'T1'), ('practice2', 'T2')]:
        deps = [] if stage == 'practice1' else [pfx + 'practice1']
        source = r.job('AC16-T-' + stage)
        clone(source['job_id'], pfx + stage, 'PRACTICED_OLD', 'CORE:S01', deps,
              'Equally practiced literal older-procedure control. Two varied '
              'practices match original T case facts, caps and instructed '
              'negative exercises. Use exactly the supplied older CORE:S01 '
              'instruction. Practice feedback may inform this practice, '
              'but must not alter the retained fixed instruction. No holdout '
              'or prior learner-answer exposure. ' + source['instructions'] +
              ' Declare six search slots; use python3.',
              practiced_older_control=True)
    clone('AC16-T-card', pfx + 'card', 'PRACTICED_OLD', 'CORE:S01',
          [pfx + 'practice1', pfx + 'practice2'],
          'Actually retain the supplied fixed_older_card exactly as literal '
          'external JSON in method_card, after reading both actual practices '
          'and replay feedback. Do not abstract new cues, conditions, '
          'counterexamples or solved answers into this card. Report actual '
          'practice/feedback exposure in the trace and handoff outside the '
          'card. This is practiced fixed-card retention, not a second '
          'adaptive card. No holdout access; use python3.',
          practiced_older_control=True, literal_older_card_retention=True)
    for case in ['HR', 'HN', 'HF', 'HX']:
        clone('AC16-FIXED-' + case, pfx + case, 'PRACTICED_OLD',
              'CORE:S01', [pfx + 'card'],
              'Fresh retrieval-assisted test of the equally practiced older '
              'literal card. Receive current frozen case plus only the fixed '
              'retained older instruction, with no practice answers or '
              'teacher conversation. Map current facts, construct at most '
              'one operation or exact applicability refusal, and declare six '
              'search slots. This controls external procedure text after '
              'practice, not transmission of learned weights or delayed '
              'unassisted human retention. Use python3.',
              practiced_older_control=True)

    clone('AC17-revision', 'COV-AC17-overfit-attack', 'OVERFIT_ATTACK',
          'AC17', ['AC17-revision'],
          'Actual adversarial overfitting pass on the immutable old and '
          'revised cards and historical failure feedback only. No current '
          'case pack, original holdout outputs or heldout facts are supplied. '
          'Test whether the single obligation delta relies on historical '
          'names/schedule, overrejects a legitimate different connection '
          'assignment, or changes the invariant. Explicitly distinguish '
          'authored procedural counterexamples from observed task results. '
          'Do not invent actual beliefs, perform case solving, or change '
          'any retained card field. Save method_card exactly equal to the '
          'received revised_card; carry criticism, unresolved applicability '
          'and unchanged invariant through the selected handoff. Six '
          'review slots; zero action candidates. Use python3.',
          role='critique', overfit_attack=True)
    for arm in ['FIXED', 'REVISED']:
        for case in ['RJ', 'RW']:
            clone('AC17-' + arm + '-' + case,
                  'COV-AC17-POSTATTACK-' + arm + '-' + case, arm,
                  'RECIPE:R07', ['COV-AC17-overfit-attack'],
                  'Fresh post-attack use of the unchanged frozen heldout '
                  'case. Both versions receive identical historical failure '
                  'feedback and the same actual overfit-attack summary; '
                  'FIXED retrieves the original compact card and REVISED '
                  'the screened unchanged one-field revision. Do not see '
                  'original heldout answers or other test outputs. Declare '
                  'six search slots; report actual spending separately. '
                  'Preserve supported applicability refusal rather than '
                  'substitute another transfer. These later tests cannot '
                  'repair the original pre-attack test order. Use python3.',
                  post_attack_revision_test=True)

    require(r.state('AC20-PRE-implementation')['valid'] and
            not r.state('AC20-PRE-service')['valid'],
            'Original valid implementation and invalid service must remain')
    pre = 'COV-AC20-PRE-service'
    clone('AC20-PRE-service', pre, 'PRE', 'ROOT:S03', [],
          'Fresh service-release/maintenance precursor on the same current '
          'J0 facts, before analog assistance. No mutual proposal, old '
          'service output, implementation output or analog bank exposure. '
          'Preserve complete release and upkeep predictions, exact task-fact '
          'provenance and at most three candidates. The original invalid '
          'service remains invalid. Six search slots; exact schema keys and '
          'python3 exclusive first save.', fresh_pre_service=True)
    for arm in ['SHARED', 'DISTINCT', 'UNION']:
        route_ids = ['COV-AC20-' + arm + '-route' + str(i) for i in [0, 1]]
        for i, jid in enumerate(route_ids):
            source = r.job('AC20-' + arm + '-route' + str(i))
            clone(source['job_id'], jid, arm, source['method_id'],
                  ['AC20-PRE-implementation', pre],
                  'Separate later source-route coverage from the unchanged '
                  'valid original implementation and new saved service '
                  'precursor. This mixes original and later draws and '
                  'cannot regrade the gated first study. Preserve both '
                  'pre-assistance pools and supplied source provenance. '
                  'Six search slots. ' + source['instructions'] +
                  ' Use python3.', fresh_route_coverage=True)
        exchange = 'COV-AC20-' + arm + '-exchange'
        clone('AC20-' + arm + '-exchange', exchange, arm, 'AC20',
              ['AC20-PRE-implementation', pre] + route_ids,
              'Join only these actual saved pre-assistance and route pools. '
              'Preserve source selectors, common facts, source union, '
              'candidate provenance and exact upstream overlap; distinguish '
              'information gain from route allocation and lexical change '
              'from causal diversity. Six search slots; source-backed '
              'no-addition/refusal is valid. Use python3.',
              fresh_route_coverage=True)
        clone('AC20-' + arm + '-builder',
              'COV-AC20-' + arm + '-builder', arm, 'AC20', [exchange],
              'Fresh reconstruction from this selected joined route summary '
              'only. Preserve pre-assistance provenance and rare feasible '
              'mechanisms, source dependencies, unknowns and information '
              'differences. At most one candidate; six declared search '
              'slots, actual spending separate. Recovery is not generation '
              'or a source-diversity benefit. Use python3.',
              fresh_route_coverage=True)
    require(len(out) == 34 and len({j['job_id'] for j in out}) == 34,
            'Exactly 34 unique prospective REVIEW4/5 coverage roles')
    return out


def base_job(j):
    """Proxy only the absent method lookup; payload restores actual identity."""
    if j.get('p10_selection'):
        proxy = copy.deepcopy(j)
        proxy['method_id'] = 'O'
        return proxy
    return j


def p10_method(r):
    names = HELPER_SOURCES[2:]
    catalog = r.p(names[0]).read_text()
    line = next(s for s in catalog.splitlines() if s.startswith('| P10 '))
    protocol = r.p(names[1]).read_text()
    passages = [s for s in protocol.splitlines()
                if s.startswith('P10:') or s.startswith('P10 compares')]
    criteria = read(r.p(names[2]))['p10']
    return {'id': 'P:P10', 'instructions': line + '\n\n' + '\n\n'.join(passages),
            'historical_exact_criteria': criteria,
            'source': str(r.p(names[0]).resolve()),
            'source_sha256s': {str(r.p(n).resolve()): sha(r.p(n)) for n in names},
            'adaptation_limit': 'Native fixed-pool presentation attempt; no '
                'fabricated legacy eligibility scores or dual-review locks.'}


def review_metadata(r, dependencies):
    """Expose omitted recorded packet/source metadata, never repair a raw."""
    rels = ['inputs/beneficiary-evidence.json', 'inputs/fixed-pool.json',
            'inputs/revision-card.v1.json', 'preparation/HOLDOUT-PARTITIONS.v1.json']
    metadata = {'source_packs': {n: {'sha256': sha(r.p(n)), 'literal': read(r.p(n))}
                               for n in rels},
                'original_freeze_utc': read(r.p('preparation/FREEZE.v1.json'))['utc'],
                'original_packet_exposures': {},
                'limit': 'Recorded literal packet and root-transcription '
                         'evidence; no independent transcript/platform '
                         'authentication or unobserved-access attestation.'}
    freeze = read(r.p('preparation/FREEZE.v1.json'))['sources']
    metadata['original_holdout_source_bindings'] = {
        case: {'path': str(r.p('inputs/cases/' + case + '.json')),
               'sha256': sha(r.p('inputs/cases/' + case + '.json')),
               'agrees_with_original_freeze': freeze.get(str(r.p(
                   'inputs/cases/' + case + '.json').resolve())) == sha(r.p(
                   'inputs/cases/' + case + '.json'))}
        for case in ['HR', 'HN', 'HF', 'HX', 'RJ', 'RW']}
    for jid in dependencies:
        path = r.p('prompts/' + jid + '.payload.json')
        if not path.exists():
            continue
        q = read(path)
        entry = {'actual_payload_sha256': sha(path),
                 'method_id': q['job']['method_id'],
                 'method_literal': q['method'],
                 'assigned_instructions': q['job'].get('instructions', ''),
                 'allowed_source_refs': q['allowed_source_refs'],
                 'direct_dependencies': q['allowed_input_job_refs']}
        for key in ['actual_beneficiary', 'fixed_pool_sha256',
                    'retrieved_card', 'absence_predicate_contract',
                    'fixed_older_card', 'matched_failure_feedback',
                    'matched_overfit_feedback', 'source_exposure_manifest']:
            if key in q:
                entry[key] = q[key]
        metadata['original_packet_exposures'][jid] = entry
    return metadata


def payload(r, j, v):
    v['job'] = j
    if j['role'] == 'review':
        v['review4_coverage_metadata'] = review_metadata(r, j['dependencies'])
        return v
    if j.get('matched_interval_absence'):
        v['absence_predicate_contract'] = {
            'predicate': 'intact_H == false at the start of every hold tick',
            'hold_ticks': v['case']['hold_ticks'],
            'initial_H_present': True, 'H_origin_parts_permitted': True,
            'listed_detach_assemble_permitted': True,
            'setup_use_outside_hold_disclosed_separately': True,
            'claim': 'Hypothetical interval-availability necessity; no '
                     'observed mistaken belief or initial/material absence.'}
    if j.get('routine_selection') or j.get('p10_selection'):
        pool = copy.deepcopy(v['fixed_pool'])
        pool.pop('frontier_rule', None)
        v['fixed_pool'] = pool
        v['pool_exposure_contract'] = {
            'original_source_sha256': sha(r.p('inputs/fixed-pool.json')),
            'delivered_sha256_canonical': hashlib.sha256(encoded(pool)).hexdigest(),
            'candidate_array_sha256_canonical': hashlib.sha256(encoded(
                pool['candidates'])).hexdigest(),
            'redaction': 'Only frontier-rule metadata withheld from new '
                         'ordinary/P10 controls; all six candidate bytes, '
                         'order, facts and caps remain identical.'}
    if j.get('routine_selection'):
        v['routine_selection_rule'] = {
            'implementation': 'Hard-feasible first; ascending non-idle '
                              'action burden then fixed pool order; max two.',
            'investigation': 'At most one unresolved source-supported '
                             'next-test option, never implementation.',
            'originality': 'Recorded separately, no frontier/reserved slot.'}
    if j.get('p10_selection'):
        v['method'] = p10_method(r)
        ordinary = r.body('COV-AC15-routine-selection')
        v['p10_fixed_assessments'] = copy.deepcopy(ordinary['selection'])
        v['p10_assessment_source_sha256'] = sha(r.p(
            'raw/COV-AC15-routine-selection.json'))
        v['p10_gates'] = {'legacy_numeric_scale_mapping': 'not fabricated',
                         'original_legacy_dual_review_locks': 'not supplied',
                         'instruction': 'Keep missing qualification fields '
                             'unknown; a qualitative visible-slot '
                             'adaptation is distinct from exact historical '
                             'ranking reproduction.'}
    if j.get('literal_older_card_retention'):
        v['fixed_older_card'] = copy.deepcopy(read(r.p(
            'inputs/methods.json'))['CORE:S01'])
    if j.get('practiced_older_control') and j['role'] == 'transfer':
        v['retrieved_card'] = r.body(j['dependencies'][0])['method_card']
        v['external_state'] = ('Only literal unchanged older card; actual '
            'practice occurred upstream, no teacher history/answers supplied.')
    if j.get('overfit_attack'):
        for key in ['received_roles', 'received_replays',
                    'common_analog_source_bank', 'forwarded_source_provenance']:
            v.pop(key, None)
        v['case'] = {'case_id': j['case_id'], 'evidence_kind': 'Card-only '
                     'attack; metadata identity is not current case exposure.',
                     'facts': []}
        v['allowed_source_refs'] = ['FB01']
        v['old_card'] = read(r.p('inputs/revision-card.v1.json'))
        v['revised_card'] = r.body('AC17-revision')['method_card']
        v['matched_failure_feedback'] = read(r.p('inputs/revision-feedback.json'))
        v['candidate_cap'] = 0
    if j.get('post_attack_revision_test'):
        attack = r.body('COV-AC17-overfit-attack')
        v['retrieved_card'] = (read(r.p('inputs/revision-card.v1.json'))
                              if j['arm'] == 'FIXED' else attack['method_card'])
        v['matched_failure_feedback'] = read(r.p('inputs/revision-feedback.json'))
        v['matched_overfit_feedback'] = attack['handoff']['summary']
        v['retained_state_contract'] = ('Fresh post-attack role; same frozen '
            'case and both feedback texts; no original heldout answers.')
    return v


def _interval_absence(case, candidate):
    intact = True
    by_tick = {a['tick']: a for a in candidate['actions']}
    for tick in range(case['end_boundary']):
        if tick in case['hold_ticks'] and intact:
            return False
        action = by_tick.get(tick, {})
        if action.get('op') == 'detach' and action.get('arg') == 'H':
            intact = False
        elif action.get('op') == 'assemble' and action.get('arg') == 'H':
            intact = True
    return True


def validate(r, j, v):
    """Additional fidelity checks; ordinary runtime validation still applies."""
    if j.get('matched_interval_absence') and j['role'] == 'builder':
        require(all(_interval_absence(r.effective_case(j), c)
                    for c in v['candidates']),
                'Final control construction must meet identical H interval absence')
    if j.get('routine_selection') or j.get('p10_selection'):
        require(v['candidates'] == [], 'Fixed-pool selector cannot generate actions')
        pool_ids = {c['id'] for c in read(r.p('inputs/fixed-pool.json'))['candidates']}
        require(set(v['selection']['implementation']) <= pool_ids and
                set(v['selection']['investigation']) <= pool_ids,
                'Only frozen pool identities may be selected')
    if j.get('p10_selection'):
        require(v['selection']['ratings'] == r.body(
                    'COV-AC15-routine-selection')['selection']['ratings'],
                'P10 must preserve the actual routine assessments unchanged')
    if j.get('literal_older_card_retention'):
        require(v['method_card'] == read(r.p('inputs/methods.json'))['CORE:S01'],
                'Older retained card must equal the literal canonical instruction')
    if j.get('overfit_attack'):
        require(v['method_card'] == r.body('AC17-revision')['method_card'] and
                v['candidates'] == [],
                'Overfit attack cannot alter the retained card or solve current cases')

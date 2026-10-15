"""Prospective minimal coverage for actual first REVIEW3 fidelity gaps.

No model calls. All original outputs/grades remain immutable. Shared-candidate
adjacent trials add deterministic replay after an actual native builder FINAL,
not separate native investigators, hidden computation or physical trials.
"""
import copy
from ac_runtime import read, save, sha, require, now, encoded, replay


PIN_ACTIONS = [
    {'tick': 0, 'op': 'tap', 'arg': 'P1'},
    {'tick': 1, 'op': 'tap', 'arg': 'P2'},
    {'tick': 7, 'op': 'pull', 'arg': 'P1'},
    {'tick': 8, 'op': 'pull', 'arg': 'P2'}]


def jobs(r):
    require(all(r.state('REVIEW-3-' + str(i))['valid'] for i in [1, 2]),
            'Both actual first REVIEW3 records are required')
    out = []
    def clone(source, jid, arm, method, dependencies, instructions, **flags):
        j = copy.deepcopy(r.job(source))
        j.update(job_id=jid, strategy_id=flags.pop('strategy_id', j['strategy_id']),
                 arm=arm, method_id=method, dependencies=dependencies,
                 instructions=instructions, **flags)
        out.append(j)
        return j
    clone('AC11-B2-J0-builder', 'COV-AC11-adjacent-builder', 'ADJACENT', 'AC11',
          ['AC11-B2-J0-critique', 'AC11-B1-J0-critique', 'AC11-B0-J0-critique'],
          'Actual post-attack adjacent trial, separate from the original '
          'unexecuted projections. Reconstruct exactly one received two-pin '
          'schedule: tap P1@0, tap P2@1, pull P1@7, pull P2@8. Use this '
          'identical construction at predeclared b=2,1,0, with adjacent '
          'pairs 2->1,1->0,0->1. Preserve every hard fact and timing; change '
          'only the soft preference. Declare the six-slot common allowance '
          'before work, distinguishing allowance from actual spending. '
          'Record the actual post-attack trial request in operation_trace '
          'and handoff. Root primitive replay after actual FINAL will execute '
          'all declared cells, so label your outcomes predictions until then. '
          'This isolates a shared construction and eligibility; it is not '
          'three fresh searches, a new mechanism or a whole-method efficacy '
          'estimate. Use python3 for the exclusive first save.',
          additional_control_coverage=True, post_attack_adjacent_trial=True)
    clone('AC09-AFTER-critique', 'COV-AC09-preservation-critique', 'AFTER', 'AC09',
          ['AC09-AFTER-first', 'AC09-AFTER-second'],
          'Fresh preservation coverage using the actual original first and '
          'second artifacts, never a repair of their bytes. Verify exact '
          'original versus revised schedules and example provenance. Distill '
          'all independent mechanisms and the precise revision in the selected '
          'summary, including six-action original sleeve/loop with restoration '
          'versus five-action revisions and unchanged two-action clip. '
          'Preserve history as provenance, not newly generated candidates. '
          'One final fresh reconstruction is permitted; do not require three '
          'final cards against its one-card bound. Use python3.',
          additional_control_coverage=True, preservation_coverage=True)
    clone('AC09-AFTER-builder', 'COV-AC09-preservation-builder', 'AFTER', 'AC09',
          ['COV-AC09-preservation-critique'],
          'Reconstruct at most one candidate from only the selected fresh '
          'summary. Preserve all received independent ideas and exact '
          'before/revised histories in handoff or revision provenance, '
          'without crediting historical records as new generation. Do not '
          'mislabel the five-action revision as the six-action first set '
          'or silently reverse a deletion. If selecting optional restoration, '
          'record it as an additional choice with its action cost. Use python3.',
          additional_control_coverage=True, preservation_coverage=True)
    names = {
        stage: 'COV-AC09-OLD-' + stage for stage in
        ['implementation', 'service', 'exchange', 'builder']}
    for stage in ['implementation', 'service', 'exchange', 'builder']:
        source = r.job('AC14-INDEPENDENT-' + stage)
        dependencies = [] if stage in ['implementation', 'service'] else (
            [names['implementation'], names['service']] if stage == 'exchange'
            else [names['exchange']])
        clone(source['job_id'], names[stage], 'OLD', 'ROOT:S03', dependencies,
              'Faithful separately admitted ROOT:S03 older control for AC09. '
              'Implementation and service are distinct actual native '
              'investigators with no mutual proposal exposure; actual common '
              'J0 facts only, no examples or analog-bank assistance. Exchange '
              'inspects both saved pools and tests scope/time/meaning before '
              'calling a contradiction. Preserve a source-supported no-tension '
              'boundary if appropriate; never invent disagreement. Distill '
              'an actual opening or refusal for the fresh builder. This has '
              'four native stages, not local serial investigator simulation. '
              'Equal hidden compute is not established. ' +
              source.get('instructions', '') + ' Use python3.',
              strategy_id='AC09', additional_control_coverage=True,
              independent_older_control=True)
    for stage in ['proposal', 'critique', 'builder']:
        jid = 'COV-AC10-CORE-O-' + stage
        dependencies = [] if stage == 'proposal' else [
            'COV-AC10-CORE-O-' + ('proposal' if stage == 'critique' else 'critique')]
        clone('AC10-T-J0-' + stage, jid, 'CORE_O', 'O', dependencies,
              'Separately admitted ordinary improvement of the unchanged '
              'verified intact-H/two-pin core. Preserve its parents, '
              'tap/pull retention mechanics, capacities and hard function. '
              'Optimize only the existing core schedule; do not substitute '
              'clip, sleeve, loop, Q retention or a whole-system replacement. '
              'Use ordinary analysis, independent criticism and the selected '
              'summary as applicable to this assigned stage. Compare source '
              'support and burden; no invented mechanism credit. Use python3.',
              additional_control_coverage=True, unchanged_core_control=True)
    clone('AC10-OLD-J0-proposal', 'COV-AC10-same-parent-boundary',
          'STRICT_PARENT', 'RECIPE:R07',
          ['AC10-T-J0-proposal', 'AC10-OLD-J0-proposal', 'AC10-OLD-J0-critique'],
          'Separately admitted strict same-parent boundary investigation. '
          'Inspect the actual verified H/two-pin core and actual T measurement '
          'insertion, and whether R07 can use that same available connection '
          'without replacing its parents. The earlier S/V replacement cannot '
          'stand in for this check. Report any genuine supported opening; '
          'otherwise give a bounded source-supported terminal refusal for '
          'this parent/link contract, not all possible systems. Do not invent '
          'theta, a useful downstream dependence, resources or unsupported '
          'mechanics. Do not treat a refusal as an executable zero-cost '
          'candidate. This boundary check does not regrade first OLD/T. '
          'Use python3.', additional_control_coverage=True,
          strict_parent_boundary=True)
    clone('AC12-defense', 'COV-AC12-actual-account-boundary',
          'ACCOUNT_BOUNDARY', 'AC12', ['AC12-defense', 'AC12-attack'],
          'Separately admitted investigation of the actual defended account. '
          'Find a source-supported failed assumption in that account if one '
          'exists. If it already rejects universal H necessity and its '
          'installation dependency remains valid, explicitly record no '
          'supported failed-dependency opening for that target. Do not '
          'manufacture a false belief, an incumbent defect or a new stressor. '
          'Preserve the valued function and the scope of refusal. The '
          'existing fresh-builder constructions/comparisons remain actual '
          'first evidence, not proof of a failed premise. Zero candidates '
          'are appropriate for a source-supported no-opening. Use python3.',
          additional_control_coverage=True, actual_account_boundary=True)
    return out


def trial_contract(r, j):
    base = r.effective_case(j)
    cases = {}
    for setting in [2, 1, 0]:
        c = copy.deepcopy(base)
        c['impact_preference'] = setting
        cases[str(setting)] = c
    return {'settings': [2, 1, 0], 'adjacent_pairs': [[2, 1], [1, 0], [0, 1]],
            'one_shared_candidate': True, 'fixed_search_allowance': 6,
            'selected_received_non_idle_actions': PIN_ACTIONS,
            'literal_trial_cases': cases,
            'limit': 'One native post-attack reconstruction; paired pure-model '
                     'replays after its actual FINAL, not independent searches '
                     'or physical/hidden-compute evidence.'}


def validate_trial(j, v):
    if not j.get('post_attack_adjacent_trial'):
        return
    require(len(v['candidates']) == 1, 'Adjacent trial requires one shared construction')
    actions = [a for a in v['candidates'][0]['actions'] if a['op'] != 'idle']
    require(actions == PIN_ACTIONS, 'Predeclared received construction must stay fixed')


def finish_trial(r, j):
    if not j.get('post_attack_adjacent_trial') or not r.state(j['job_id'])['valid']:
        return
    v = read(r.p('raw/' + j['job_id'] + '.json'))
    contract = trial_contract(r, j)
    candidate = v['candidates'][0]
    rows = [{'setting': setting, 'literal_case': contract['literal_trial_cases'][str(setting)],
             'replay': replay(contract['literal_trial_cases'][str(setting)], candidate)}
            for setting in contract['settings']]
    path = r.p('replays/' + j['job_id'] + '.adjacent-settings.json')
    save(path, {'utc': now(), 'job_id': j['job_id'], 'candidate_id': candidate['id'],
                'actual_native_raw_sha256': sha(r.p('raw/' + j['job_id'] + '.json')),
                'actual_native_FINAL_receipt_sha256': sha(r.p('receipts/jobs/' + j['job_id'] + '.native-final.json')),
                'post_attack_contract': contract, 'trial_replays': rows,
                'evidence': 'Actual deterministic stipulated-model execution after observed native FINAL; no additional native call or physical trial.'})
    save(r.p('receipts/jobs/' + j['job_id'] + '.adjacent-lock.json'),
         {'utc': now(), 'path': str(path), 'sha256': sha(path),
          'actual_raw_sha256': sha(r.p('raw/' + j['job_id'] + '.json'))})


def verify_trials(r):
    for j in r.coverage_plan():
        if not j.get('post_attack_adjacent_trial') or not r.state(j['job_id'])['valid']:
            continue
        lock = read(r.p('receipts/jobs/' + j['job_id'] + '.adjacent-lock.json'))
        require(sha(lock['path']) == lock['sha256'], 'Adjacent first replay bytes changed')
        require(sha(r.p('raw/' + j['job_id'] + '.json')) == lock['actual_raw_sha256'],
                'Adjacent native construction changed')
        saved = read(lock['path'])
        require(saved['post_attack_contract'] == trial_contract(r, j), 'Adjacent contract drift')
        v = read(r.p('raw/' + j['job_id'] + '.json'));validate_trial(j, v)
        require(saved['actual_native_FINAL_receipt_sha256'] == sha(r.p('receipts/jobs/' + j['job_id'] + '.native-final.json')),
                'Adjacent actual FINAL observation changed')
        for row in saved['trial_replays']:
            expected = saved['post_attack_contract']['literal_trial_cases'][str(row['setting'])]
            require(row['literal_case'] == expected and row['replay'] == replay(expected, v['candidates'][0]),
                    'Adjacent replay no longer reproduces')
        require([row['setting'] for row in saved['trial_replays']] == [2, 1, 0],
                'A declared adjacent cell is missing')
    return True

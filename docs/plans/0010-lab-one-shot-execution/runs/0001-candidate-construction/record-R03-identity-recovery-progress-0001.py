"""Preserve unavailable process evidence and synchronize scoped API49 progress."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    assert not Path('/proc/365370').exists()
    assert not (RUN / 'API48-controls11-terminal-0001.json').exists()
    assert not (BASE / 'api48-current-checks-v1/receipts/controls-0001.json').exists()
    log = RUN / 'API48-controls11-0001.log'
    raw = log.read_text()
    successes = [line for line in raw.splitlines() if line.endswith(' ... ok')]
    assert len(successes) == 7
    assert 'test_08_actual_policy_revocation_inside_fact_scope' in raw
    observation = RUN / 'API48-unavailable-driver-observation-0001.json'
    put(observation, {'schema_version': 'lab-unavailable-process-observation/v1-candidate',
        'observed_at': datetime.now(timezone.utc).isoformat(), 'prior_PID': 365370,
        'prior_PID_absent': True, 'prior_tool_session': 25516, 'tool_result': 'Unknown process id 25516',
        'actual_exit_code': None, 'cause_established': False, 'full_suite_verdict_established': False,
        'controls_completed_log_cases': 7, 'controls_log_binding': bind(log),
        'driver_log_binding': bind(RUN / 'API48-serialized-public-qualification-0001.log'),
        'completed_typed_terminal_binding': bind(RUN / 'API48-typed8-terminal-0001.json'),
        'guarded_exit_and_cleanup_proven_for_interrupted_controls': False,
        'old_keys_workspaces_and_claims_not_inspected_or_reused': True,
        'no_old_session_or_agent_memory_restored': True,
        'authority_effect': 'none', 'task_complete': False})
    context = RUN / 'context-R03-API49-interruption-recovery-0001.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R03', 'strict_coverage': 'PASS',
        'superseded_orchestration_context_binding': bind(RUN / 'context-R03-API49-public-typed-0001.json'),
        'source_bindings': [bind(observation), bind(RUN / 'authorization.json'),
                            bind(BASE / 'api49-typed-checks-v1/source-manifest.json')],
        'write_scope': ['fresh isolated API49 test fixtures', 'new run evidence only'],
        'selected_orchestration': 'The prior process is absent with no exit status or complete controls verdict. Start a separately logged fresh API49 typed10 suite after source/dependency byte checks. Keep all unfinished predecessor suite obligations.',
        'constraints': ['Do not rerun a live process or overwrite any old result.',
            'Original test assertions, absolute Assignment periods, real clocks and source/cleanup checks are unchanged.',
            'Recreate absent code only; never restore an old Agent, key, memory, fixture or operation claim.',
            'All prior incomplete suites and all original plan criteria remain outstanding.',
            'Existing candidate development authorization applies; final owner outcome remains R08.'],
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False})
    parent = BASE / 'api-v48/receipts/R03-0084.json'
    old = load(parent)
    rows = {row['path']: row for row in old['files']}
    for name in ['api-v49', 'typed-host-composition-v4', 'api48-typed-checks-v2', 'api49-typed-checks-v1']:
        manifest = BASE / name / 'source-manifest.json'
        for row in load(manifest)['files']:
            rows[row['path']] = row
        row = bind(manifest)
        rows[row['path']] = row
    extras = [parent, observation, context, Path(__file__).resolve(),
        RUN / 'ARE-R03-construction-boundaries-0085.json', RUN / 'run-API49-recovery-qualification-0001.py',
        RUN / 'restore-selected-native-code-0003.py', RUN / 'native-code-restoration-0003.json',
        RUN / 'native-code-restoration-0003.stdout', RUN / 'native-code-restoration-0003.stderr',
        RUN / 'API48-typed8-terminal-0001.json', RUN / 'API48-typed8-0001.log',
        BASE / 'api48-typed-checks-v1/receipts/checks-0001.json',
        BASE / 'api48-typed-checks-v1/receipts/wire-0001.json']
    for stem in ['API48-typed-binding-join-checks-0001', 'typed-preclaim-join-checks-0001']:
        extras.extend([RUN / (stem + '.json'), RUN / (stem + '.log')])
    for name in ['API48-typed-binding-successor-static-0001.json', 'typed-preclaim-join-static-0001.json']:
        extras.append(RUN / name)
    for path in extras:
        row = bind(path)
        rows[row['path']] = row
    assert load(RUN / 'native-code-restoration-0003.json')['native_byte_identity']
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    proofs = [load(RUN / name) for name in ['API48-typed-binding-join-checks-0001.json', 'typed-preclaim-join-checks-0001.json']]
    assert [proof['actual_cases'] for proof in proofs] == [6, 41]
    assert all(p['result'] == 'PASS' and p['actual_public_calls'] == 0 for p in proofs)
    api = BASE / 'api-v49'
    value = {**old, 'files': [rows[k] for k in sorted(rows)], 'parent_progress_binding': bind(parent),
        'source_binding': bind(api / 'source-manifest.json'), 'profile_binding': bind(api / 'contract-profile.json'),
        'change': 'Preserved API48 typed8 actual FAIL:7PASS/1FAIL/0ERROR. Joined independently selected proposal/successor identities;6 full original wire/noncollapse pure checks and41 preclaim/inventory checks PASS. API49 frozen. Prior controls process unavailable after7 completed log cases, exit unknown. Exact absent native code restored; fresh isolated successor qualification selected without reusing old claims.',
        'typed_operator_host_composition_authored': True, 'typed_operator_public_qualified': False,
        'typed_identity_pure_actual_cases': 47, 'API49_full_public_runtime_qualified': False,
        'API48_typed_full_result': {'actual_exit_code': 1, 'PASS': 7, 'FAIL': 1, 'ERROR': 0},
        'API48_negative_cases_qualification_ceiling': 'Downstream-negative expectations may have passed at an earlier identity refusal. The corrected full successor is required.',
        'unavailable_driver_observation_binding': bind(observation),
        'current_serialized_public_driver_binding': bind(RUN / 'run-API49-recovery-qualification-0001.py'),
        'current_full_suites': ['API49 fresh authenticated typed10 selected; actual result pending',
            'API48 interrupted controls11 remains without a full verdict', 'Original failure18 and strict full146 outstanding'],
        'current_full_public_suite_verdict': None,
        'claim_ceiling': 'Scoped candidate implementation and47 pure checks; no corrected public runtime verdict, genuine semantic owner review, assigned Machine qualification, operational grant, admission or full plan completion.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    value['remaining_obligations'] = list(old['remaining_obligations']) + [
        'Qualify corrected API49 typed10 and every original current suite without weakening assertions.',
        'Preserve API48 unknown exit and interrupted controls evidence; no guarded exit, cleanup or full result is inferred.']
    path = api / 'receipts/R03-0085.json'
    put(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
                      'pure_cases': 47, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()

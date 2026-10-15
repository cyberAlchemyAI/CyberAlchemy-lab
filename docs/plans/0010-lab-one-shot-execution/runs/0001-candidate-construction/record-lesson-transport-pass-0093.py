"""Record actual API52 zero-Lesson transport qualification with verified wire joins."""
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


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    predecessor = BASE / 'api-v52/receipts/R03-0092.json'
    old = load(predecessor)
    check = BASE / 'api52-lesson-checks-v1/receipts'
    report_path = check / 'checks-0001.json'
    report = load(report_path)
    assert bind(report_path)['sha256'] == '0343d1795efd2d466c71306d681fd3d48ec797109ba84ac5cf75cf8fd7b394d6'
    assert report['result'] == 'PASS' and report['actual_cases'] == 3 and report['errors'] == report['failures'] == 0
    assert report['full_selected_suite_completed'] and report['source_guarded_exit_completed']
    assert report['source_sha256'] == old['source_binding']['sha256']
    assert report['profile_sha256'] == old['profile_binding']['sha256']
    wire = load(check / 'wire-0001.json')
    assert len(wire) == report['actual_public_calls'] == 10
    calls = [(row.get('original_call', row.get('actual_machine_call')), row['reply']) for row in wire]
    openings = [reply['message'] for call, reply in calls if call['operation'] == 'session.open' and reply['kind'] == 'result']
    assert len(openings) == 3 and len({row['session_ref'] for row in openings}) == 3
    assert len({row['agent_instance_ref'] for row in openings}) == 3
    machine_calls = [(call, reply) for call, reply in calls if call['operation'] == 'lesson.select']
    assert len(machine_calls) == 4
    positive = [(call, reply) for call, reply in machine_calls if reply.get('kind') == 'result']
    assert len(positive) == 1
    call, reply = positive[0]
    result = reply['message']
    assert result['schema_version'] == 'lab-lesson-selection/v1-candidate' and result['items'] == []
    assert result['session_ref'] == call['message']['actor']['session_ref'] == openings[0]['session_ref']
    assert result['assignment'] == call['message']['assignment'] == openings[0]['assignment']
    handler = BASE / 'api-v52/lesson_selection.py'
    assert reply['handler_binding'] == {'ref': handler.relative_to(ROOT).as_posix(), 'sha256': bind(handler)['sha256']}
    errors = [reply for _, reply in machine_calls if reply.get('kind') == 'error']
    assert len(errors) == 2 and errors[0]['message']['code'] == 'unauthorized'
    disposed = machine_calls[-1][1]
    assert disposed['schema_version'] == 'lab-api-transport-error/v1-candidate' and disposed['code'] == 'unauthenticated-channel'
    assert not disposed['effect_may_have_started']
    terminal = RUN / 'API52-lesson3-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'session_id': 29782,
        'initial_chunk_id': 'cf7cb3', 'final_chunk_id': '67d2d5', 'actual_exit_code': 0,
        'result': 'PASS', 'actual_cases': 3, 'actual_public_calls': 10, 'failures': 0, 'errors': 0,
        'full_selected_suite_completed': True, 'source_guarded_exit_completed': True,
        'report_binding': bind(report_path), 'log_binding': bind(check / 'actual-0001.log'),
        'wire_binding': bind(check / 'wire-0001.json'), 'source_binding': old['source_binding'],
        'profile_binding': old['profile_binding'], 'authority_effect': 'none',
        'nonempty_signed_source_qualified': False, 'task_complete': False, 'goal_complete': False})
    rows = {row['path']: row for row in old['files']}
    for row in report['files']:
        rows[row['path']] = row
    for path in (predecessor, report_path, terminal, Path(__file__).resolve()):
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    value = {**old, 'files': [rows[key] for key in sorted(rows)], 'parent_progress_binding': bind(predecessor),
        'change': 'Actual API52 lesson transport3 PASS/exit0,10 wire calls, three distinct real Agent/Session openings, exact successful zero-Lesson selection, spoof/foreign-Assignment refusal and disposed-peer unauthenticated transport. Source exit guard complete. Package transfer successor61 pure cases already complete. Nonempty source, whole lesson behavior and complete API remain unqualified.',
        'lesson_selection_public_suite_verdict': 'PASS', 'lesson_selection_empty_inventory_transport_qualified': True,
        'lesson_selection_actual_live_Session_qualified': False,
        'lesson_selection_actual_live_Session_qualification_scope': 'Three real actual transport cases on this exact zero-Lesson source only; nonempty/generalized behavior unqualified.',
        'lesson_selection_nonempty_signed_source_qualified': False,
        'lesson_selection_actual_public_calls': 10, 'lesson_selection_real_Sessions_opened': 3,
        'lesson_selection_public_report_binding': bind(report_path), 'lesson_selection_public_terminal_binding': bind(terminal),
        'lesson_selection_positive_empty_result_count': 1, 'lesson_selection_negative_machine_call_count': 3,
        'remaining_obligations': [item for item in old['remaining_obligations'] if not item.startswith('Observe same API52 lesson3')],
        'claim_ceiling': 'API52 actual zero-Lesson/live-Session transport3 PASS with10 wire calls and full source exit. Package transfer61 synthetic pure cases PASS. No nonempty/generalized lesson qualification, new public export/import handler, semantic import validity, assigned Machine write authority, complete API, genuine pilot, admission or full plan.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = BASE / 'api-v52/receipts/R03-0093.json'
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
        'actual_lesson_cases': 3, 'actual_wire_calls': 10, 'package_pure_cases': 61, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()

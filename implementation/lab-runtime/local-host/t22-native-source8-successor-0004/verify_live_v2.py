"""Cold replay of the public T22 API42 Session observation, without API execution."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import live_session_v2 as L


EXPECTED_API_SOURCE = '41aab1ef39fd93c33e2313a19466f4755a8ea14389c1d6abcfdb4ce461be3f50'
EXPECTED_API_PROFILE = '043138382a4f3bc94e7c5ad00c957e6b1f91d0dd80cbb335941ade05ef942e4d'
EXPECTED_OPERATIONS = ['context.get', 'session.open', 'session.inspect', 'session.close']


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def assess(value, episode, selected):
    need(value['schema_version'] == 'lab-T22-native-session-inspection/v2'
         and value['status'] == 'PASS-native-Session-consumption'
         and value['authority_effect'] == 'none'
         and value['original_t22_complete'] is False
         and value['contest_outcome'] is None and value['lesson_outcome'] is None,
         'Session claim ceiling differs')
    need(value['native_family_chain_sha256'] == L.sha(L.seal_chain.RESULT.read_bytes()),
         'native family chain changed')
    selected_runner = L.checked_file(L.RUNNER_SELECTION,
                                     value['selected_runner_binding']['sha256'])
    need(value['selected_runner_binding']['path'] == L.RUNNER_SELECTION.relative_to(L.ROOT).as_posix()
         and json.loads(selected_runner)['runner_sha256'] == L.sha(Path(L.__file__).read_bytes()),
         'preselected runner binding differs')
    need(value['api_source_binding']['sha256'] == EXPECTED_API_SOURCE
         and value['api_profile_binding']['sha256'] == EXPECTED_API_PROFILE,
         'selected API42 binding differs')
    for row in (value['api_source_binding'], value['api_profile_binding']):
        L.checked_file(L.ROOT / row['path'], row['sha256'])
    manifest = json.loads(L.checked_file(L.ROOT / value['api_source_binding']['path'], EXPECTED_API_SOURCE))
    api_prefix = str(Path(value['api_source_binding']['path']).parent) + '/'
    code_rows = sorted((row for row in manifest['files']
                        if row['path'].startswith(api_prefix) and row['path'].endswith('.py')),
                       key=lambda row: row['path'])
    for row in code_rows:
        L.checked_file(L.ROOT / row['path'], row['sha256'])
    need(value['captured_api_code'] == {
        'python_modules': len(code_rows),
        'selected_code_rows_sha256': L.sha(json.dumps(code_rows, sort_keys=True, separators=(',', ':')).encode())},
         'captured API42 Python code selection differs')
    need(value['selected_work_sha256'] == L.seal_chain.work_check.WORK_SHA,
         'selected signed Work differs')
    obs = value['api_call_observations']
    need(type(obs) is list and [row['operation'] for row in obs] == EXPECTED_OPERATIONS,
         'actual native operation sequence differs')
    for row in obs:
        need(set(row) == {'operation', 'request_sha256', 'reply_sha256', 'reply'}
             and row['reply_sha256'] == L.sha(episode.compact(row['reply']))
             and row['reply']['operation'] == row['operation']
             and row['reply']['kind'] == 'result'
             and row['reply']['request_binding']['sha256'] == row['request_sha256'],
             'native reply/request byte binding differs')
    delivery, opened, inspected, closed = (row['reply']['message'] for row in obs)
    need(value['context_view_header'] == delivery['context_view']
         and value['context_delivery_source_cut'] == delivery['source_cut']
         and value['context_delivery_binding'] == opened['context_delivery_binding']
         and value['context_delivery_binding'] == {
             'ref': 'context-delivery:' + delivery['context_view']['version_ref'],
             'sha256': L.sha(episode.compact(delivery))},
         'fresh Context delivery/Session opening differs')
    work = [row for row in delivery['included_refs'] if row['carrier_ref'] == 'cal.artifact-type.work/v1']
    need(len(work) == 1 and work[0]['byte_sha256'] == value['selected_work_sha256'],
         'fresh Context delivery omitted exact Work')
    need(value['session_ref'] == opened['session_ref'] == inspected['session_ref'] == closed['session_ref']
         and value['session_started_at'] == opened['started_at']
         and value['session_expires_at'] == opened['expires_at']
         and value['session_note_count'] == 2
         and value['session_inspected'] is True and value['session_closed'] is True
         and value['memory_zeroed'] is True and closed['discarded_memory'] is True,
         'native Session lifecycle/disposal differs')
    view = value['public_bounded_view']
    opened_at = datetime.fromisoformat(view['opened_at']).timestamp()
    need(episode.bounded_view(selected, opened_at) == view,
         'bounded State projection no longer reconstructs from selected sources')
    view_raw = episode.compact(view)
    need(value['bounded_view_sha256'] == L.sha(view_raw)
         and value['bounded_view_bytes'] == len(view_raw)
         and len(view_raw) <= 16 * 1024
         and datetime.fromisoformat(view['expires_at']) > datetime.fromisoformat(opened['started_at'])
         and datetime.fromisoformat(view['opened_at']) >= datetime.fromisoformat(opened['started_at']),
         'bounded State view byte/time binding differs')
    need(value['report'] == L.observed_report(episode, selected, view, view_raw, delivery,
                                             opened, inspected, closed, True),
         'source-pinned discrepancy report differs')
    return {'status': 'PASS-cold-public-output-replay',
            'receipt_sha256': L.sha(L.seal_chain.canonical(value)),
            'api_operations': EXPECTED_OPERATIONS,
            'native_workflow_run_observed': False,
            't31_transition_count_added': 0}


def verify(expected_sha):
    chain = L.seal_chain.calculate()
    need(L.seal_chain.RESULT.read_bytes() == L.seal_chain.canonical(chain),
         'selected Source-to-Context construction receipt changed')
    episode = L.selected_episode()
    selected = episode.selection(L.ROOT)
    raw = L.checked_file(L.RESULT, expected_sha)
    value = json.loads(raw)
    need(raw == L.seal_chain.canonical(value), 'Session receipt serialization differs')
    return assess(value, episode, selected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.receipt_sha256), sort_keys=True))

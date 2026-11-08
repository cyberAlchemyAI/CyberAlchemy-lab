"""Cold validation of the selected d95 Session phase receipt."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ('implementation/lab-runtime/local-host/source8-current-fixture/instances/'
          'legacy-local-d95e3b741ca86f02/source/source-manifest.json',
          'fa55046b2d5ff60713500c5466fd356552fa75ceec53fe53635a81e141798019')
API = ('product/lab/release-candidates/v1/interface/'
       'api-integration-v33-t03-one-lesson-native-v4-0004/source-manifest.json',
       '822bef0481a1ce2e050be1324a1059e9bd3f018b96fb290fb10776fbc648bc64')
PROFILE = ('product/lab/release-candidates/v1/interface/'
           'api-integration-v33-t03-one-lesson-native-v4-0004/contract-profile.json',
           '0d0fa9fd9f461a7e9c2f3775b397051d1518f23005a75483a8bf6143eaa7e02b')
SELECTION = ('implementation/lab-runtime/local-host/t35-phase-observer-native-v4-0001/'
             'selected-boundaries.json',
             'c4dd2b82e76a65aa0dfcddd7c727440b42e701d798a51a8ad7f45744b49f10ee')
PERIOD = ('implementation/lab-runtime/local-host/source8-current-fixture/instances/'
          'legacy-local-d95e3b741ca86f02/source/packages/0001/period.json',
          '7409f858261a79bd249c76d63c9c47686f99efff9d5db9448fd1aff3ce7d4683')


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def utc(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    need(result.tzinfo is not None and result.utcoffset().total_seconds() == 0,
         'non-UTC phase time')
    return result.astimezone(timezone.utc)


def verify(result: dict, root: Path = ROOT) -> None:
    for path, expected in (SOURCE, API, PROFILE, SELECTION, PERIOD):
        source = root / path
        need(source.is_file() and not source.is_symlink() and
             sha(source.read_bytes()) == expected, 'selected phase input changed: ' + path)
    period = json.loads((root / PERIOD[0]).read_bytes())
    need(result['schema_version'] == 'lab-T35-current-source8-session-phases-native-v4/v1' and
         result['selected_source_manifest_sha256'] == SOURCE[1] and
         result['selected_api_source_manifest_sha256'] == API[1] and
         result['selected_boundary_selection_sha256'] == SELECTION[1] and
         result['source_period_expires_at'] == period['expires_at'] and
         result['runner_sha256'] == sha((HERE / 'run.py').read_bytes()) and
         result['authority_effect'] == 'none', 'phase origin differs')
    for key in ('expired_request_refused_without_live_resource',
                'session_opened_and_guarded', 'session_closed_and_memory_disposed',
                'owned_temporary_fixture_removed'):
        need(result[key] is True, 'phase outcome missing: ' + key)
    need([row['operation'] for row in result['calls']] ==
         ['context.get', 'session.open', 'session.open', 'session.close'] and
         [row['reply_kind'] for row in result['calls']] ==
         ['result', 'error', 'result', 'result'], 'phase call order differs')
    for row in result['calls']:
        for key in ('request_sha256', 'reply_sha256'):
            need(type(row[key]) is str and len(row[key]) == 64 and
                 all(c in '0123456789abcdef' for c in row[key]),
                 'phase call digest invalid')
    run_start, run_end = utc(result['started_at_utc']), utc(result['completed_at_utc'])
    source_end = utc(result['source_period_expires_at'])
    reader_end = utc(result['reader_lease_expires_at'])
    context_end = utc(result['context_delivery_expires_at'])
    session_end = utc(result['session_lease_expires_at'])
    need(run_start < run_end < session_end <= context_end <= reader_end <= source_end and
         abs((run_end - run_start).total_seconds() - result['monotonic_elapsed_seconds']) < .25,
         'phase lease order or run clocks differ')
    observation = result['observation']
    events = observation['events']
    need(observation['schema_version'] == 'lab-t35-explicit-boundary-observation/v1' and
         observation['measurement_class'] == 'selected-candidate' and
         observation['boundary_selection_sha256'] == SELECTION[1] and
         utc(observation['source_expires_at']) == source_end and
         observation['callback_count'] == 6 and
         observation['pure_scope_boundary_count'] == 0 and
         observation['authority_effect'] == 'none' and
         [row['name'] for row in events] ==
         ['Service.call', 'ContextSessions.delivery', 'Service.call',
          'Service.call', 'LiveReader.guard', 'Service.call'],
         'selected phase event inventory differs')
    previous_end = run_start
    for row in events:
        start, end = utc(row['started_at_utc']), utc(row['completed_at_utc'])
        strictest = min(source_end, session_end if row['name'] == 'LiveReader.guard' else reader_end)
        need(row['kind'] == 'callback' and row['status'] == 'PASS' and
             row['exception_class'] is None and row['expired_at_completion'] is False and
             row['pure_scope_boundaries_observed'] == 0 and
             utc(row['strictest_observed_expires_at']) == strictest and
             previous_end <= start <= end < strictest and end <= run_end and
             abs((end - start).total_seconds() - row['monotonic_elapsed_seconds']) < .05,
             'selected phase event clock or status differs')
        previous_end = end


if __name__ == '__main__':
    verify(json.loads((HERE / 'RESULT.json').read_bytes()))
    print('PASS: d95 native-v4 six selected Session phase callbacks')

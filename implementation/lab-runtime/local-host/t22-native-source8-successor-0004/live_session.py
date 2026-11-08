"""Run actual API42 Context/Session on the signed T22 family once selected.

This runner uses public fixture interfaces and real service guards. It replaces
only the test suite's per-call observation hook so a run does not write into the
selected API package; it does not replace a source, auth, policy or API guard.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time

# Isolated Python excludes the script directory. Select only this owned
# task-local module directory for the sealed chain and Work verifier.
_TASK_MODULE_DIR = Path(__file__).resolve().parent
if _TASK_MODULE_DIR.is_symlink() or any(parent.is_symlink() for parent in _TASK_MODULE_DIR.parents):
    raise ValueError('linked T22 module directory')
sys.path.insert(0, str(_TASK_MODULE_DIR))
import seal_chain


ROOT = seal_chain.ROOT
HERE = Path(__file__).resolve().parent
EPISODE = ROOT / 'implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002/episode.py'
EPISODE_SHA = 'a3aac58fe32f2921a014a15fca95549f96bc0d2ad269021cea23925e1e5c08ea'
RESULT = HERE / 'LIVE-SESSION-0001.json'


def sha(raw): return hashlib.sha256(raw).hexdigest()


def checked_file(path, expected):
    path = Path(path)
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('selected executable path linked')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode): raise ValueError('selected executable not regular')
        with os.fdopen(fd, 'rb', closefd=False) as stream: raw = stream.read()
    finally:
        os.close(fd)
    if sha(raw) != expected: raise ValueError('selected executable bytes changed')
    return raw


def chunks(raw, maximum=4096):
    if type(raw) is not bytes or not raw or len(raw) > 65536 or maximum != 4096:
        raise ValueError('Session note budget invalid')
    return [raw[i:i + maximum] for i in range(0, len(raw), maximum)]


def selected_episode():
    raw = checked_file(EPISODE, EPISODE_SHA)
    name = '_cal_T22_episode_selected'
    module = type(sys)(name)
    module.__file__ = str(EPISODE)
    sys.modules[name] = module
    exec(compile(raw, str(EPISODE), 'exec', dont_inherit=True), module.__dict__)
    return module


def selected_api(api_dir, source_sha, profile_sha):
    if not sys.flags.isolated: raise ValueError('run with python3 -I -B')
    api_dir = Path(api_dir)
    if not api_dir.is_absolute() or not api_dir.is_relative_to(ROOT / 'product/lab/release-candidates/v1/interface'):
        raise ValueError('API42 path outside selected interface root')
    if api_dir.is_symlink() or any(parent.is_symlink() for parent in api_dir.parents):
        raise ValueError('API42 linked path')
    manifest = json.loads(checked_file(api_dir / 'source-manifest.json', source_sha))
    checked_file(api_dir / 'contract-profile.json', profile_sha)
    rows = {row['path']: row['sha256'] for row in manifest['files']}
    for filename in ('__init__.py', 'guard.py', 'test_custody_sessions.py'):
        path = api_dir / filename
        relative = path.relative_to(ROOT).as_posix()
        if relative not in rows: raise ValueError('API42 entry module not source-selected')
        checked_file(path, rows[relative])
    name = '_cal_T22_api42_' + source_sha[:16]
    spec = importlib.util.spec_from_file_location(name, api_dir / '__init__.py', submodule_search_locations=[str(api_dir)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    guard = importlib.import_module(name + '.guard')
    guard.verify(source_sha)
    test = importlib.import_module(name + '.test_custody_sessions')
    if test.source.CURRENT_LEGACY_NAME != 'completion-legacy:legacy-local-710362c855a8a11c':
        raise ValueError('API42 selected another native family')
    return test


def observed_report(episode, selected, view, view_raw, delivery, opened, inspected, closed, zeroed):
    if not zeroed or closed.get('discarded_memory') is not True:
        raise ValueError('Session RAM disposal not observed')
    report = episode.expected_report(selected, view, sha(view_raw))
    report['schema_version'] = 'lab-T22-native-api30-inspection-report/v1'
    report['native_lab_session'] = True
    report['context_delivery_binding'] = opened['context_delivery_binding']
    if report['context_delivery_binding']['ref'] != 'context-delivery:' + delivery['context_view']['version_ref']:
        raise ValueError('opened Session delivery identity differs')
    report['session_ref'] = opened['session_ref']
    report['session_inspected'] = inspected['session_ref'] == opened['session_ref']
    report['session_closed'] = closed['session_ref'] == opened['session_ref']
    report['memory_zeroed'] = True
    if not report['session_inspected'] or not report['session_closed']:
        raise ValueError('Session inspection or close differs')
    return report


def run(api_dir, source_sha, profile_sha):
    chain = seal_chain.calculate()
    if chain['status'] != 'PASS-native-family-construction': raise ValueError('native chain not selected')
    if seal_chain.RESULT.read_bytes() != seal_chain.canonical(chain):
        raise ValueError('sealed native chain receipt changed')
    episode = selected_episode()
    selected = episode.selection(ROOT)
    test = selected_api(api_dir, source_sha, profile_sha)
    # The upstream unittest runner injects this exact profile pin before
    # setUpClass; reproduce that selection in this single-case harness.
    test.PROFILE = profile_sha
    case = test.Sessions(methodName='test_01_actual_private_memory_erased')
    setup = False
    class_ready = False
    try:
        class_ready = True
        test.Sessions.setUpClass()
        case.setUp(); setup = True
        # The public service and schemas are unchanged. Only avoid writing
        # per-call unittest observations into the immutable API42 source tree.
        def invoke(call):
            raw = test.compact(call)
            reply = case.service.call(raw)
            if not case.schemas.valid('api-reply', reply): raise ValueError('native API reply schema refused')
            if reply['request_binding']['sha256'] != test.source.sha(raw):
                raise ValueError('native API request byte binding differs')
            if reply['contract_profile_binding'] != case.schemas.profile_binding:
                raise ValueError('native API profile binding differs')
            if reply['kind'] != 'result': raise ValueError('native API operation refused: ' + call['operation'] + ': ' + str(reply.get('code')))
            return reply
        case.invoke = invoke
        opened, opening_call = case.opening_success()
        delivery = case.delivery_result
        if opened['context_delivery_binding'] != opening_call['message']['context_delivery_binding']:
            raise ValueError('Session opening/delivery binding differs')
        selected_work = [row for row in delivery['included_refs'] if row['carrier_ref'] == 'cal.artifact-type.work/v1']
        if len(selected_work) != 1 or selected_work[0]['byte_sha256'] != seal_chain.work_check.WORK_SHA:
            raise ValueError('native delivery did not select API30 Work')
        # This local source-pinned State projection is generated at the actual
        # Session clock, after a fresh native Context delivery and open.
        view = episode.bounded_view(selected, time.time())
        view_raw = episode.compact(view)
        if len(view_raw) > 16 * 1024 or datetime.fromisoformat(view['expires_at']) <= datetime.now(timezone.utc):
            raise ValueError('bounded Project State view expired before consumption')
        resource = case.service.sessions.live[opened['session_ref']]
        held = []
        for chunk in chunks(view_raw):
            resource.note(chunk)
            held.append(resource.memory[-1])
        if b''.join(bytes(item) for item in resource.memory) != view_raw:
            raise ValueError('fresh native Session did not consume exact State bytes')
        inspected = case.success(case.inspection(opened['session_ref']))
        closed = case.success(case.closing(opened, inspected))
        zeroed = resource.closed and resource.memory == [] and all(item == bytearray(len(item)) for item in held)
        report = observed_report(episode, selected, view, view_raw, delivery, opened, inspected, closed, zeroed)
        result = {'schema_version': 'lab-T22-native-session-inspection/v1', 'status': 'PASS-native-Session-consumption',
                  'api_source_binding': {'path': (Path(api_dir) / 'source-manifest.json').relative_to(ROOT).as_posix(), 'sha256': source_sha},
                  'api_profile_binding': {'path': (Path(api_dir) / 'contract-profile.json').relative_to(ROOT).as_posix(), 'sha256': profile_sha},
                  'native_family_chain_sha256': sha(seal_chain.RESULT.read_bytes()),
                  'context_delivery_source_cut': delivery['source_cut'],
                  'selected_work_sha256': selected_work[0]['byte_sha256'],
                  'bounded_view_sha256': sha(view_raw), 'bounded_view_bytes': len(view_raw),
                  'session_ref': opened['session_ref'], 'session_started_at': opened['started_at'],
                  'session_expires_at': opened['expires_at'], 'session_note_count': len(held),
                  'session_inspected': True, 'session_closed': True, 'memory_zeroed': zeroed,
                  'report': report, 'contest_outcome': None, 'lesson_outcome': None,
                  'original_t22_complete': False, 'authority_effect': 'none'}
    finally:
        if setup:
            try: case.tearDown()
            finally: case.doCleanups()
        if class_ready: test.Sessions.doClassCleanups()
    raw = seal_chain.canonical(result)
    fd = os.open(RESULT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return {'status': result['status'], 'sha256': sha(raw)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-dir', type=Path, required=True)
    parser.add_argument('--api-source-sha256', required=True)
    parser.add_argument('--api-profile-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.api_dir, args.api_source_sha256, args.api_profile_sha256), sort_keys=True))


if __name__ == '__main__': main()

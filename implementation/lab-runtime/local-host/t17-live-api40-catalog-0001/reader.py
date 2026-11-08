"""One disposable API40 Base read episode for Paperclip's process adapter."""

import argparse
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import os
import stat
import sys
import time
import types

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
API = INTERFACE / 'api-integration-v40-current-t06-0001'
RUNNER = INTERFACE / 'paperclip-runner-v3/runner.py'
SOURCE_SHA = '45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219'
PROFILE_SHA = 'cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614'
RUNNER_SHA = 'a1de38b075fc40f137e51785f7841990f4aaf83fa445cb2f5ea06bc3d27b60b9'
SOURCE_NAME = 'completion-legacy:legacy-local-947e6c2a5b3d10f8'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected):
    path = Path(path)
    need(path.is_file() and not any(parent.is_symlink() for parent in (path, *path.parents)), 'linked selected file')
    raw = path.read_bytes()
    need(sha(raw) == expected, 'selected file changed')
    return raw


def helper():
    raw = checked(RUNNER, RUNNER_SHA)
    module = types.ModuleType('t17_selected_paperclip_runner_v3')
    module.__file__ = str(RUNNER)
    exec(compile(raw, str(RUNNER), 'exec'), module.__dict__)
    checked(RUNNER, RUNNER_SHA)
    return module


def selected_config(path):
    path = Path(path)
    state = path.lstat()
    need(path.is_absolute() and path.is_relative_to('/tmp') and not path.is_relative_to(ROOT)
         and stat.S_ISREG(state.st_mode) and state.st_uid == os.getuid()
         and stat.S_IMODE(state.st_mode) == 0o600 and state.st_size < 16384,
         'owned private selection required')
    return json.loads(path.read_bytes())


def count_workspace(policy):
    workspace = Path(policy['workspace']['root'])
    need(workspace.is_relative_to('/tmp') and workspace.is_dir(), 'owned workspace required')
    objects = list((workspace / 'objects').iterdir())
    journal = list((workspace / 'journal').iterdir())
    unexpected = [entry for entry in journal if entry.name != '.session-custody.lock']
    need(not unexpected, 'read episode wrote an effect or unexpected journal entry')
    lock = workspace / 'journal/.session-custody.lock'
    if lock in journal:
        state = lock.lstat()
        need(stat.S_ISREG(state.st_mode) and state.st_uid == os.getuid()
             and stat.S_IMODE(state.st_mode) == 0o600 and state.st_nlink == 1
             and state.st_size == 0 and lock.read_bytes() == b'',
             'selected Session custody lock differs')
    return {'objects': len(objects), 'effect_journal': len(unexpected),
            'session_custody_lock': int(lock in journal)}


def run(config):
    started = time.monotonic()
    R = helper()
    source_raw = checked(API / 'source-manifest.json', SOURCE_SHA)
    checked(API / 'contract-profile.json', PROFILE_SHA)
    source = R.parse(source_raw)
    rows = {row['path']: row['sha256'] for row in source['files']}
    for name in ('__init__.py', 'guard.py'):
        path = API / name
        need(rows.get(path.relative_to(ROOT).as_posix()) == sha(path.read_bytes()), 'API bootstrap changed')
    api_name = '_t17_selected_api40'
    spec = importlib.util.spec_from_file_location(api_name, API / '__init__.py', submodule_search_locations=[str(API)])
    api = importlib.util.module_from_spec(spec)
    sys.modules[api_name] = api
    spec.loader.exec_module(api)
    guard = __import__(api_name + '.guard', fromlist=['verify'])
    guard.verify(SOURCE_SHA)
    protocol = __import__(api_name + '.protocol', fromlist=['Schemas'])
    schemas = protocol.Schemas(PROFILE_SHA)
    policy_raw = R.selected_file(config['policy'], config['policy_sha256'], private=True)
    policy = R.parse(policy_raw)
    need(policy['workspace']['max_actions'] == 1 and policy['source_name'] == SOURCE_NAME
         and policy['authority_effect'] == 'none', 'effective local read budget differs')
    before = count_workspace(policy)
    need(before == {'objects': 0, 'effect_journal': 0, 'session_custody_lock': 0},
         'workspace was not fresh')
    key_raw = R.selected_file(config['reader_key'], config['reader_key_sha256'], private=True)
    key = serialization.load_pem_private_key(key_raw, password=None)
    need(isinstance(key, Ed25519PrivateKey), 'Ed25519 key required')
    plan = R.validate_plan(R.parse(R.selected_file(config['plan'], config['plan_sha256'])))
    need(plan['steps'] == [{'operation': 'catalog.get', 'selectors':
                            {'carrier_refs': [], 'include_relations': True, 'limit': 20, 'page_cursor': None}}],
         'only status/catalog selected')
    deadline = min(datetime.now(timezone.utc) + timedelta(seconds=config['timeout_seconds']),
                   datetime.fromisoformat(policy['expires_at'].replace('Z', '+00:00'))).isoformat()
    child = R.Child([sys.executable, '-I', '-B', str(API / 'serve.py'), '--source-sha256', SOURCE_SHA,
                     '--policy', str(config['policy']), '--policy-sha256', config['policy_sha256'],
                     '--protocol-profile-sha256', PROFILE_SHA],
                    time.monotonic() + config['timeout_seconds'])
    observations = []
    cut = None
    context = None
    handler = API / 'handlers.py'
    expected_handler = {'ref': handler.relative_to(ROOT).as_posix(), 'sha256': rows[handler.relative_to(ROOT).as_posix()]}
    try:
        challenge = child.receive()
        need(schemas.valid('reader-authentication', challenge) and
             challenge.get('schema_version') == 'lab-local-reader-challenge/v1-candidate' and
             challenge['policy_sha256'] == config['policy_sha256'], 'API40 challenge differs')
        child.send({'schema_version': 'lab-local-reader-proof/v1-candidate', 'challenge': challenge,
                    'signature': base64.b64encode(key.sign(R.encoded(challenge))).decode()})
        key = None
        auth = child.receive()
        need(schemas.valid('reader-authentication', auth) and
             auth.get('schema_version') == 'lab-local-reader-authenticated/v1-candidate', 'API40 authentication refused')
        context = auth['context']
        need(context['principal_ref'] == policy['principal_ref'] and context['scope_refs'] == policy['scope_refs']
             and context['accept_client_supplied_authority_context'] is False,
             'authenticated context differs')
        for operation, case in [('lab.status', 'positive'), ('catalog.get', 'positive'),
                                ('lab.status', 'wrong-scope'), ('catalog.get', 'wrong-context')]:
            call = R.build_call(protocol, schemas, context, operation, cut, {}, deadline)
            if case == 'wrong-scope':
                call['message']['scope_refs'] = ['scope:outside']
            elif case == 'wrong-context':
                call['caller_context_ref'] = 'context:outside'
            need(schemas.valid('api-call', call), 'selected API40 call shape differs')
            raw = R.encoded(call)
            child.send(call)
            reply = child.receive()
            need(schemas.valid('api-reply', reply) and reply['call_id'] == call['call_id']
                 and reply['operation'] == operation
                 and reply['request_binding']['sha256'] == sha(raw)
                 and reply['contract_profile_binding'] == schemas.profile_binding
                 and reply['trusted_context_binding'] == auth['trusted_context_binding']
                 and reply['handler_binding'] == expected_handler,
                 'API40 reply binding differs')
            message = reply['message']
            if case != 'positive':
                need(reply['kind'] == 'error' and message['code'] == 'unauthorized', 'unauthorized Base read not refused')
            else:
                need(reply['kind'] == 'result' and message['authority_effect'] == 'none', 'positive Base read refused')
                if cut is None:
                    cut = message['source_cut']
                else:
                    need(message['source_cut'] == cut, 'Base source cut moved')
                if operation == 'catalog.get':
                    need(message['contract_entries'], 'catalog lacked selected entries')
            observations.append({'operation': operation, 'case': case,
                                 'kind': reply['kind'], 'code': message.get('code'),
                                 'request_sha256': sha(raw), 'reply_sha256': sha(R.encoded(reply))})
    finally:
        key = None
        child.close()
    need(child.process.returncode == 0, 'API40 child did not close cleanly')
    guard.verify(SOURCE_SHA)
    after = count_workspace(policy)
    need(after == {'objects': 0, 'effect_journal': 0, 'session_custody_lock': 1},
         'read episode changed workspace beyond Session custody lock')
    return {'schema_version': 'lab-t17-paperclip-api40-read-episode/v1', 'result': 'PASS',
            'api_source_sha256': SOURCE_SHA, 'api_profile_sha256': PROFILE_SHA,
            'runner_v3_sha256': RUNNER_SHA, 'source_cut_sha256': sha(R.encoded(cut)),
            'observations': observations, 'workspace_before': before, 'workspace_after': after,
            'api40_child_exit_code': child.process.returncode,
            'paperclip_api_called': False, 'lab_mutations_requested': 0,
            'human_usefulness_observed': False, 'authority_effect': 'none',
            'elapsed_seconds': round(time.monotonic() - started, 3)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    try:
        result = run(selected_config(args.config))
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except Exception as error:
        print(json.dumps({'schema_version': 'lab-t17-paperclip-api40-read-refusal/v1', 'result': 'FAIL',
                          'error_class': type(error).__name__, 'authority_effect': 'none'}, sort_keys=True))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

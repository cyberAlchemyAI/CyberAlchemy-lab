"""Owned technical startup driver; key bodies remain outside the repository.

Preparation and startup are separate explicit commands. Startup selects a new
Action lease in the actual child process; it never reconstructs Session RAM.
"""
import argparse
import base64
import copy
from datetime import datetime, timezone
import fcntl
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import select
import stat
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
ACTION_FILES = ('source.json', 'source.signature', 'grant.json', 'status.json', 'ledger-pins.json')


def need(value, message):
    if not value:
        raise ValueError(message)


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, 'duplicate selected field')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: need(False, 'nonfinite JSON'))


def identity(value):
    return [value.st_dev, value.st_ino, value.st_uid, stat.S_IMODE(value.st_mode)]


def stamp(value):
    return [*identity(value), value.st_size, value.st_mtime_ns, value.st_ctime_ns]


def directory(path, expected):
    path = Path(path)
    need(path.is_absolute() and str(path) == os.path.normpath(str(path)), 'canonical absolute locator required')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = nxt
        need(identity(os.fstat(fd)) == expected and expected[2:] == [os.getuid(), 0o700], 'private root changed')
        return fd
    except BaseException:
        os.close(fd)
        raise


def protected(selector, root, root_identity, limit=16 * 1024 * 1024):
    need(set(selector) == {'path', 'identity', 'sha256'}, 'closed protected selector required')
    path = Path(selector['path']); root = Path(root)
    need(path.is_absolute() and str(path) == os.path.normpath(str(path)) and path.is_relative_to(root), 'owned private path required')
    parent = directory(root, root_identity); descriptors = [parent]
    try:
        parts = path.relative_to(root).parts
        need(parts, 'private leaf required')
        for part in parts[:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            descriptors.append(parent)
            value = os.fstat(parent)
            need(value.st_uid == os.getuid() and stat.S_IMODE(value.st_mode) == 0o700, 'private parent changed')
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and identity(before) == selector['identity']
                 and selector['identity'][2:] == [os.getuid(), 0o600] and before.st_size <= limit, 'private leaf changed')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                raw = stream.read(limit + 1)
            need(len(raw) <= limit and stamp(before) == stamp(os.fstat(fd))
                 == stamp(os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)), 'private input changed during capture')
            need(sha256(raw).hexdigest() == selector['sha256'], 'private digest changed')
        finally:
            os.close(fd)
        # Reopen every ancestor against its retained descriptor before returning.
        fresh = directory(root, root_identity)
        try:
            for index, part in enumerate(parts[:-1], 1):
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fresh)
                os.close(fresh); fresh = nxt
                need(identity(os.fstat(fresh)) == identity(os.fstat(descriptors[index])), 'private parent detached')
            need(stamp(os.stat(parts[-1], dir_fd=fresh, follow_symlinks=False)) == stamp(before), 'private leaf detached')
        finally:
            os.close(fresh)
        return raw
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def selector(path):
    path = Path(path)
    value = path.lstat()
    need(stat.S_ISREG(value.st_mode) and stat.S_IMODE(value.st_mode) == 0o600, 'private regular file required')
    parent = directory(path.parent, identity(path.parent.lstat()))
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            need(stamp(before) == stamp(value) and before.st_size <= 16 * 1024 * 1024, 'private selector capture changed')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                raw = stream.read(16 * 1024 * 1024 + 1)
            need(len(raw) <= 16 * 1024 * 1024 and stamp(os.fstat(fd)) == stamp(value)
                 == stamp(os.stat(path.name, dir_fd=parent, follow_symlinks=False)), 'private selector bytes changed')
        finally:
            os.close(fd)
        later = directory(path.parent, identity(os.fstat(parent))); os.close(later)
        return {'path': str(path), 'identity': identity(value), 'sha256': sha256(raw).hexdigest()}
    finally:
        os.close(parent)


def read_record(path, pin):
    path = Path(path); root = path.parent; expected_root = identity(root.lstat())
    need(root.name.startswith('cal-T06-branch-fixtures-') and root.parent == Path('/tmp'), 'owned fixture root required')
    row = selector(path); need(row['sha256'] == pin, 'independent private selection pin differs')
    value = parse(protected(row, root, expected_root))
    need(value['root'] == str(root) and value['root_identity'] == expected_root, 'private selection root differs')
    return value


def load_key(row, record):
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    key = load_pem_private_key(protected(row, record['root'], record['root_identity'], 16384), password=None)
    need(isinstance(key, Ed25519PrivateKey), 'Ed25519 private credential required')
    return key


def replace_owned(path, expected, raw, root, root_identity):
    # Only the six declared files inside the newly owned Action root are replaced.
    protected(expected, root, root_identity)
    path = Path(path); need(path.parent == Path(root), 'owned direct Action leaf required')
    parent = directory(root, root_identity); temporary = '.handoff-' + uuid.uuid4().hex
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        need(identity(os.stat(path.name, dir_fd=parent, follow_symlinks=False)) == expected['identity'], 'Action preimage detached')
        fresh = directory(root, root_identity); os.close(fresh)
        os.replace(temporary, path.name, src_dir_fd=parent, dst_dir_fd=parent); os.fsync(parent)
    finally:
        os.close(parent)
    row = selector(path); protected(row, root, root_identity)
    return row


def handoff_materials(initial, fresh, signer):
    source = parse(initial['source.json']); status = parse(initial['status.json'])
    grant = parse(initial['grant.json']); policy = parse(initial['channel-policy.json'])
    need(set(fresh) == {'instance', 'session'} and all(type(x) is str and x for x in fresh.values()), 'fresh public lease attribution required')
    source = copy.deepcopy(source); source['runtime_bindings'] = copy.deepcopy(fresh)
    refs = source['refs']; handles = {refs['agent-instance']: fresh['instance'], refs['agent-session']: fresh['session']}
    need(set(source['initial_status']['runtime_handle_bindings']) == set(handles)
         and set(status['runtime_handle_bindings']) == set(handles), 'original attribution shape differs')
    source['initial_status']['runtime_handle_bindings'] = handles
    status = copy.deepcopy(status); status['runtime_handle_bindings'] = handles
    source_raw = compact(source); grant = copy.deepcopy(grant); grant['source_sha256'] = sha256(source_raw).hexdigest()
    grant_raw = compact(grant); policy = copy.deepcopy(policy)
    policy['source_binding'] = {'ref': 'action-source:' + sha256(source_raw).hexdigest(), 'sha256': sha256(source_raw).hexdigest()}
    policy['grant_binding'] = {'ref': 'action-grant:' + sha256(grant_raw).hexdigest(), 'sha256': sha256(grant_raw).hexdigest()}
    return {'source.json': source_raw, 'source.signature': base64.b64encode(signer.sign(source_raw)),
            'status.json': compact(status), 'grant.json': grant_raw, 'operator-policy.json': compact(policy),
            'ledger-pins.json': initial['ledger-pins.json']}


def make_handoff(record, config, config_pin, request):
    need(request['schema_version'] == 'lab-composite-fresh-session-request/v1-candidate'
         and request['configuration_sha256'] == config_pin and request['authority_effect'] == 'none', 'wrong live child handoff request')
    action = record['branches']['actions']; signer = load_key(record['source_signer'], record)
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    need(base64.b64encode(signer.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
         == action['source_public_key'], 'original source signer credential differs')
    original = parse(protected(record['initial_inputs'], record['root'], record['root_identity']))
    initial = {name: base64.b64decode(raw, validate=True) for name, raw in original.items()}
    grant = parse(initial['grant.json']); end = grant['expires_at']
    need(grant['not_before'] <= time.time() < end and time.time() < request['lease_expires_at'] <= end, 'fixed original grant period cannot support actual lease')
    materials = handoff_materials(initial, request['fresh_lease'], signer)
    files = {}
    for name in ACTION_FILES:
        if name == 'ledger-pins.json':
            files[name] = action['files'][name]
            protected(files[name], action['workspace_root'], action['root_identity'])
        else:
            files[name] = replace_owned(Path(action['workspace_root']) / name, action['files'][name],
                                        materials[name], action['workspace_root'], action['root_identity'])
    policy_path = Path(action['workspace_root']) / 'operator-policy.json'
    need(not policy_path.exists(), 'new owned handoff policy leaf required')
    fd = os.open(policy_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(materials['operator-policy.json']); stream.flush(); os.fsync(stream.fileno())
    files['operator-policy.json'] = selector(policy_path)
    protected(files['operator-policy.json'], action['workspace_root'], action['root_identity'])
    packet = {'schema_version': 'lab-composite-current-handoff/v1-candidate', 'configuration_sha256': config_pin,
              'fresh_lease': copy.deepcopy(request['fresh_lease']), 'files': files}
    authorizations = {}
    for kind in ('custody', 'grant', 'policy'):
        issuer = config['handoff']['issuers'][kind]
        key = load_key(record['issuers'][kind]['private_key'], record)
        need(base64.b64encode(key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
             == issuer['public_key'], 'independent issuer credential differs')
        signed = {'schema_version': 'lab-composite-current-selection-authorization/v1-candidate',
                  'selection_kind': kind, 'purpose': 'candidate-technical-current-selection', 'authority_effect': 'none',
                  'issuer_authorization_binding': issuer['authorization_binding'], 'handoff': packet}
        authorizations[kind] = {'signature_base64': base64.b64encode(key.sign(compact(signed))).decode()}
    return {**packet, 'authorizations': authorizations}


class Frames:
    def __init__(self, stream):
        self.stream = stream; self.buffer = b''

    def receive(self, deadline):
        while b'\n' not in self.buffer:
            remaining = deadline - time.monotonic()
            need(remaining > 0 and select.select([self.stream.fileno()], [], [], remaining)[0], 'actual child observation deadline exceeded')
            raw = os.read(self.stream.fileno(), 65536)
            need(raw, 'actual child ended before expected frame'); self.buffer += raw
            need(len(self.buffer) <= 2 * 1024 * 1024, 'child output frame budget exceeded')
        raw, self.buffer = self.buffer.split(b'\n', 1)
        need(len(raw) <= 1024 * 1024, 'child output frame too large')
        return parse(raw)


def send(stream, value):
    stream.write(compact(value) + b'\n'); stream.flush()


def configure(record, args):
    sdk = Path(args.sdk_directory)
    need(sdk == INTERFACE / 'composite-operator-v1-completion-0001/revision-0002', 'independently selected revision-0002 SDK required')
    manifest_raw = (sdk / 'source-manifest.json').read_bytes()
    need(sha256(manifest_raw).hexdigest() == args.sdk_source_sha256, 'SDK source manifest differs')
    api = INTERFACE / 'api-integration-v17'
    bootstrap = []
    for path in sorted([*sdk.glob('*.py'), *[api / name for name in ('guard.py', '__init__.py', 'source-manifest.json', 'contract-profile.json', 'integration-members.json')]]):
        bootstrap.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha256(path.read_bytes()).hexdigest()})
    config = {'schema_version': 'lab-composite-operator-config/v2-candidate', 'purpose': 'owned-candidate-rehearsal', 'authority_effect': 'none',
              'provisioning_binding': {'path': args.provisioning_path, 'sha256': args.provisioning_sha256},
              'source': {'directory': str(api), 'source_sha256': record['source_sha256'], 'profile_sha256': record['profile_sha256'],
                         'members_sha256': sha256((api / 'integration-members.json').read_bytes()).hexdigest(), 'bootstrap_bindings': bootstrap},
              'dependencies': {'selection': {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json',
                                            'sha256': '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'},
                               'installation': str(INTERFACE / 'runtime-dependencies-v2-completion-0001/installations/0004')},
              'branches': record['branches'],
              'handoff': {'contract': 'fresh-session-current-source-handoff/v1-candidate', 'startup_seconds': 300,
                          'issuers': {kind: {key: value for key, value in row.items() if key != 'private_key'} for kind, row in record['issuers'].items()}},
              'transport': {'max_frames': 128, 'max_wire_bytes': 16 * 1024 * 1024, 'max_frame_bytes': 1024 * 1024, 'max_response_bytes': 1024 * 1024}}
    # The independently selected original constructors produced these pinned
    # branches. The launcher repeats its own complete semantic preflight.
    raw = compact(config); path = Path(record['root']) / 'operator-config.json'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return config, path, sha256(raw).hexdigest()


def run(record, args):
    config, path, config_pin = configure(record, args)
    lock = os.open(args.lease_lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    child = None; rows = []; started = time.monotonic(); exit_code = None
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        sdk = Path(args.sdk_directory)
        stderr_path = Path(record['root']) / 'operator-stderr.bin'
        errfd = os.open(stderr_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(errfd, 'wb') as errors:
            installation = Path(config['dependencies']['installation'])
            child = subprocess.Popen([str(installation / 'lib/abi/ld-linux-x86-64.so.2'), '--inhibit-cache',
                                      '--library-path', str(installation / 'lib/abi'), str(installation / 'bin/python'),
                                      '-I', '-X', 'utf8', '-B', '-S', str(sdk / 'launch.py'), '--launcher-source-sha256', args.sdk_source_sha256,
                                      '--config', str(path), '--config-sha256', config_pin], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=errors, pass_fds=(lock,), env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
            frames = Frames(child.stdout); observation_deadline = time.monotonic() + 600
            request = frames.receive(observation_deadline)
            need(request.get('schema_version') == 'lab-composite-fresh-session-request/v1-candidate', 'actual full34 launch did not request fresh lease')
            rows.append({'event': request['schema_version'], 'elapsed_seconds': time.monotonic() - started})
            send(child.stdin, make_handoff(record, config, config_pin, request))
            challenges = frames.receive(observation_deadline)
            need(challenges.get('schema_version') == 'lab-composite-challenges/v1-candidate'
                 and set(challenges['challenges']) == {'base', 'actions', 'governance'}, 'actual independent branch challenges absent')
            for kind in ('base', 'actions', 'governance'):
                challenge = challenges['challenges'][kind]; key = load_key(record['reader_keys'][kind], record)
                if kind == 'governance':
                    # Selected Governance-v4 dependencies.encoded is P.compact.
                    encoded = compact(challenge)
                    proof = {'challenge': challenge, 'signature_base64': base64.b64encode(key.sign(encoded)).decode()}
                else:
                    proof = {'schema_version': 'lab-local-reader-proof/v1-candidate' if kind == 'base' else 'lab-local-action-proof/v1-candidate',
                             'challenge': challenge, 'signature': base64.b64encode(key.sign(compact(challenge))).decode()}
                send(child.stdin, {'schema_version': 'lab-composite-branch-proof/v1-candidate', 'branch': kind,
                                   'proof_base64': base64.b64encode(compact(proof)).decode()})
            ready = frames.receive(observation_deadline)
            need(ready.get('schema_version') == 'lab-composite-ready/v1-candidate' and ready['catalog_operation_count'] == 34
                 and ready['composition'] == 'Base28+Action3+Governance3' and ready['authority_effect'] == 'none', 'actual common full34 dispatcher readiness absent')
            rows.append({'event': ready['schema_version'], 'elapsed_seconds': time.monotonic() - started,
                         'composition': ready['composition'], 'catalog_operation_count': 34})
            # EOF requires actual owned channel/service cleanup and source exit
            # guards. It executes no dispatch, admission or checkpoint effect.
            child.stdin.close(); exit_code = child.wait(timeout=120)
            need(exit_code == 0, 'actual full34 owned shutdown refused')
        return {'schema_version': 'lab-T06-actual-full34-startup/v1-candidate', 'status': 'PASS', 'authority_effect': 'none',
                'actual_owner_outcome': None, 'process_exit_code': exit_code, 'events': rows,
                'elapsed_seconds': time.monotonic() - started, 'configuration_sha256': config_pin,
                'dispatch_operations_executed': 0, 'whole_API_qualified': False, 'actual_admitted_provisioning': False,
                'private_credentials_public_exported': False}
    finally:
        if child is not None and child.poll() is None:
            # Close only this driver's own child input; keep an observable live
            # handle if its guarded cleanup has not yet returned.
            if not child.stdin.closed:
                child.stdin.close()
            try:
                child.wait(timeout=120)
            except subprocess.TimeoutExpired:
                print(json.dumps({'status': 'LIVE-CLEANUP', 'owned_process_id': child.pid}), flush=True)
        os.close(lock)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--branch-selection', required=True); parser.add_argument('--branch-selection-sha256', required=True)
    parser.add_argument('--sdk-directory', required=True); parser.add_argument('--sdk-source-sha256', required=True)
    parser.add_argument('--provisioning-path', required=True); parser.add_argument('--provisioning-sha256', required=True)
    parser.add_argument('--lease-lock', required=True)
    args = parser.parse_args()
    record = read_record(args.branch_selection, args.branch_selection_sha256)
    result = run(record, args)
    # This public output contains no physical private selectors, keys, source
    # bodies, grant bodies, Session RAM, nonce challenges or wire contexts.
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
